from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
import httplib2
import datetime
import json
import hashlib
import logging
import logging.handlers

from urllib import urlencode

settings = json.load(open("settings.json"))
storage = Storage('a_credentials_file')

logger = logging.getLogger('google-audit-log')
logger.setLevel("INFO")
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)


credentials = storage.get()
if not credentials:
    flow = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/admin.reports.audit.readonly',
                               redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    auth_uri = flow.step1_get_authorize_url()
    print auth_uri
    code = raw_input("Auth token: ")
    credentials = flow.step2_exchange(code)
    storage.put(credentials)


http = httplib2.Http()
http = credentials.authorize(http)


def get_data_page(http, system, start, end, page_token = None):
    url = "https://www.googleapis.com/admin/reports/v1/activity/users/all/applications/%s?startTime=%s&endTime=%s&maxResults=1000" % (system, start, end)
    logger.debug("Opening page %s", url)
    if page_token:
        url = url + "&pageToken=%s" % page_token
    resp, content = http.request(url)
    data = json.loads(content)
    if data.get("items") is None:
        return None
    return data

def get_data(http, system, start, end):
    a = True
    page_token = None
    data_all = {"items": []}
    while a or page_token:
        a = False
        data = get_data_page(http, system, start, end, page_token)
        if not data:
            return data_all
        data_all["items"].extend(data.get("items"))
        page_token = data.get("nextPageToken")
    logger.debug("Successfully downloaded %s entries", len(data_all))
    return data_all



def get_docs_data(start, end):
    logger.info("Starting docs download from %s to %s", start, end)
    data = get_data(http, "docs", start, end) #"2013-05-29T00:00:00.000Z", "2013-05-30T23:59:59.000Z")
    processed_data = []
    for item in data["items"]:
        d = {}
        d["actor"] = item["actor"]["email"]
        d["action"] = item["events"][0]["name"]
        if not item["events"][0]["parameters"][0]["name"] == "doc_id":
            continue
        d["doc_id"] = item["events"][0]["parameters"][0]["value"]
        d["remote_ip"] = item.get("ipAddress")
        d["timestamp"] = item["id"]["time"].replace("Z", "")
        d["raw_data"] = json.dumps(item)
        d["hash"] = hashlib.md5(json.dumps(d)).hexdigest()
        processed_data.append(d)
        if len(processed_data) > 50:
            post_to_login("gdocs", processed_data)
            processed_data = []
    if len(processed_data) > 0:
        post_to_login("gdocs", processed_data)
    logger.info("Finished docs processing")
    save_timestamp("gdocs", {"largest": (datetime.datetime.utcnow() - datetime.timedelta(seconds=3600)).strftime("%Y-%m-%dT%H:%M:%S.000Z")})

def get_admin_data(start, end):
    logger.info("Starting admin download from %s to %s", start, end)
    data = get_data(http, "admin", start, end) # "2013-05-29T00:00:00.000Z", "2013-05-30T23:59:59.000Z")
    processed_data = []
    for item in data.get("items", []):
        for event in item.get("events", []):
            d = {}
            d["actor"] = item["actor"]["email"]
            d["domain"] = item.get("ownerDomain")
            d["remote_ip"] = item.get("ipAddress")
            d["timestamp"] = item["id"]["time"].replace("Z", "")
            d["raw_data"] = json.dumps(item)
            d["event_type"] = event["type"]
            d["event_code"] = event["name"]
            for a in event.get("parameters", []):
                 if a["name"] == "USER_EMAIL":
                     d["user_email"] = a["value"]
                 if a["name"] == "GROUP_EMAIL":
                     d["group_email"] = a["value"]

            d["hash"] = hashlib.md5(json.dumps(d)).hexdigest()
            processed_data.append(d)
        if len(processed_data) > 50:
            post_to_login("gadmin", processed_data)
            processed_data = []

    if len(processed_data) > 0:
        post_to_login("gadmin", processed_data)
    logger.info("Finished admin processing")
    save_timestamp("gadmin", {"largest": (datetime.datetime.utcnow() - datetime.timedelta(seconds=3600)).strftime("%Y-%m-%dT%H:%M:%S.000Z")})


def load_timestamp(system):
    try:
        loaded_timestamp = json.load(open("timestamps-%s.json" % system))
    except:
        loaded_timestamp = {"largest": "2000-01-01T00:00:00.000Z"}
    return loaded_timestamp

def save_timestamp(system, timestamp):
    json.dump(timestamp, open("timestamps-%s.json" % system, "w"))


def post_to_login(system, data):
    last_timestamp = data[-1].get("timestamp")+"Z"
    http_post = httplib2.Http()
    resp, content = http_post.request(settings["server_url"] + system, "POST", urlencode({"entries": json.dumps(data)}))
    loaded_timestamp = load_timestamp(system)
    if loaded_timestamp["largest"] < last_timestamp:
        loaded_timestamp["largest"] = last_timestamp
        save_timestamp(system, loaded_timestamp)



def main():
    today = datetime.datetime.utcnow()
    get_docs_data(load_timestamp("gdocs")["largest"], today.strftime("%Y-%m-%dT23:59:59.999Z"))
    get_admin_data(load_timestamp("gadmin")["largest"], today.strftime("%Y-%m-%dT23:59:59.999Z"))

if __name__ == '__main__':
    main()
