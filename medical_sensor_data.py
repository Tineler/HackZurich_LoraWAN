#!/usr/bin/env python3

import urllib
import psycopg2
import xmltodict

from http.server import BaseHTTPRequestHandler, HTTPServer



# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
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

    def insert_data(self, data):
        data_dict = xmltodict.parse(data)
        uplink_data = data_dict.get('DevEUI_uplink')
        time = uplink_data.get('Time')
        dev_eui = uplink_data.get('DevEUI')
        payload_hex = uplink_data.get('payload_hex')
        payload = bytes.fromhex(payload_hex).decode('utf-8')
        try:
            conn = psycopg2.connect("dbname=hackzurich")
            cursor = conn.cursor()
            cursor.execute("insert into sensor_message (dev_eui, time, payload, packet) values (%s, %s, %s, %s)",
                           (dev_eui, time, payload, data))
            cursor.connection.commit()
            conn.close()
        except Exception as e:
            print("DB Insert failed: %s" % e)




if __name__ == '__main__':
    server_address = ('0.0.0.0', 8001)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()
