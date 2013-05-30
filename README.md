Google Audit log downloader
===========================

Downloads Google audit logs using Admin SDK Reports API and POST entries to another server.

In our setup, audit logs are downloaded by server running GADS, and pushed to another server accessible
by all users. This way, OAuth tokens are better protected.

Setup
-----
Install oauth2client and httplib2:

```
pip install oauth2client httplib2 
```

Create settings.json:

```json
{"server_url": "https://server.address.example.com/app/update?system="}
```

Create new application to [Google API console](https://code.google.com/apis/console/). Enable Admin SDK
from "Services" tab. Go to "API Access", and create new OAuth token. Choose "Client ID for installed
applications". Click "Download JSON" and put client_secret.json to program folder.

On the first run, program prints out authorization URL. Open that in the browser with admin access to 
your Google Apps. Click "Allow" and paste token back to the console, and hit enter.

License
-------
MIT license.

Copyright (C) 2013 Olli Jarva <olli@jarva.fi>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and 
associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial 
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
