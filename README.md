Google Audit log downloader
===========================

Downloads Google audit logs using Admin SDK Reports API and POST entries to another server.

In our setup, audit logs are downloaded by server running GADS, and pushed to another server accessible 
by all users. This way, OAuth tokens are better protected.

Setup
-----
Install oauth2client (pip install oauth2client) and httplib2 (pip install httplib2).

Create settings.json:

{"server_url": "https://server.address.example.com/app/update?system="}

Create new application to Google API console: https://code.google.com/apis/console/ . Enable Admin SDK 
from "Services" tab. Go to "API Access", and create new OAuth token. Choose "Client ID for installed 
applications". Click "Download JSON" and put client_secret.json to program folder.

On the first run, program prints out URL. Open that in the browser with admin access to your Google Apps.
Click "Allow" and paste token back to the console, and hit enter.
