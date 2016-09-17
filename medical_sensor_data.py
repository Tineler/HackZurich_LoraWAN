#!/usr/bin/env python2

import xmltodict
import httplib, urllib
import BaseHTTPServer


# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # not used, just a sample
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()

        # Send message back to client
        message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')

        # Print on stdout
        print(post_data)

        # And insert into the db
        self.insert_data(post_data)

    def send_data(self, data):
        data_dict = xmltodict.parse(data)
        uplink_data = data_dict.get('DevEUI_uplink')
        dev_eui = uplink_data.get('DevEUI')

        if dev_eui == "9CD90BB52B6A1D03" or dev_eui == "9CD90BB52B6A1D04":
            time = uplink_data.get('Time')
            payload = uplink_data.get('payload_hex')

            params = urllib.urlencode({'@dev_eui': dev_eui, '@payload': payload, '@time': time})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            try:
                print(params)
                conn = httplib.HTTPConnection("medicaldatamanagerapp.mybluemix.net", 80)
                conn.request("POST", "/sensor-message", params, headers)
                response = conn.getresponse()
                print(response.status)
            except Exception as e:
                print("DB Insert failed: %s" % e)

if __name__ == '__main__':
    server_address = ('0.0.0.0', 8001)
    httpd = BaseHTTPServer.HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()
