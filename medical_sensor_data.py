#!/usr/bin/env python3

import urllib
import psycopg2
import xmltodict
import httplib, urllib
import BaseHTTPServer
from datetime import datetime

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
        # And insert into the db
        self.insert_data(post_data)

    def insert_data(self, data):
        data_dict = xmltodict.parse(data)
        uplink_data = data_dict.get('DevEUI_uplink')
        dev_eui = uplink_data.get('DevEUI')

        if dev_eui == "9CD90BB52B6A1D03" or dev_eui == "9CD90BB52B6A1D04":
            time = uplink_data.get('Time')
            date_object = datetime.strptime(time[:time.find('+')], '%Y-%m-%dT%H:%M:%S.%f')
            date = date_object.strftime('%Y-%m-%dT%H:%M:%SZ')
            payload_hex = uplink_data.get('payload_hex')
            print("dev_eui = {}".format(dev_eui))
            print("payload = {}".format(payload_hex))
            action_id = int(payload_hex[0:2])
            print("action id = {}".format( action_id))
            params = urllib.urlencode({'action_id': action_id, 'dev_eui': dev_eui, 'payload': payload_hex, 'time': date})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            try:
                conn = httplib.HTTPConnection("medicaldatamanagerapp.mybluemix.net", 80)
                conn.request("POST", "/sensor-message", params, headers)
                response = conn.getresponse()
                print("response status = {}".format(response.status))
                conn.close()
            except Exception as e:
                print("DB Insert failed: %s" % e)




if __name__ == '__main__':
    server_address = ('0.0.0.0', 8001)
    httpd = BaseHTTPServer.HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()
