from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json
class CustomHandler(BaseHTTPRequestHandler):
    file_path = '../monitor_data.json'
    execute_file_path = '../execute_data.json'
    # HTTP Get - Monitor Endpoint 
    def monitor(self):
        if self.path == '/monitor':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # read simulation data values from the monitor_data.json file 
            with open(self.file_path, 'r') as json_file:
                data = json.load(json_file)
            self.wfile.write(json.dumps(data))
            
    # HTTP Get - Monitor Schema Endpoint 
    
    def monitor_schema(self):
        schema = json.load(open('app/http_server/monitor_schema.json'))
        if self.path == '/monitor_schema':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')   
            self.end_headers()
            # return the defined monitor json schema
            self.wfile.write(json.dumps(schema))    
              
     # HTTP Get - Adaptation Options Endpoint 
     
    def adaptation_options(self):
        schema = json.load(open('app/http_server/adaptation_options.json'))
        if self.path == '/adaptation_options':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # return the defined adaptation options
            self.wfile.write(json.dumps(schema))

    # HTTP Get - Adaptation Options Endpoint 
    def adaptation_options_schema(self):
        schema = json.load(open('app/http_server/adaptation_options_schema.json'))
        if self.path == '/adaptation_options_schema':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
             # return the defined adaptation options json schema
            self.wfile.write(json.dumps(schema))
            
    # HTTP Get - Execute Schema Endpoint 
    
    def execute_schema(self):
        schema = json.load(open('app/http_server/execute_schema.json'))
        if self.path == '/execute_schema':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # return the defined execute json schema
            self.wfile.write(json.dumps(schema))
            
    # HTTP Put - Execute Endpoint 
    
    def execute(self):
        if self.path == '/execute':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            # write simulation data values to the execute_data.json file  
            with open(self.execute_file_path, 'w') as json_file:
                json_file.write(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Custom PUT route not found')
            
# Get Endpoints

    def do_GET(self):
        print("Call reached GET")
        self.monitor()
        self.monitor_schema()
        self.adaptation_options()
        self.adaptation_options_schema()
        self.execute_schema()
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'{}')
# Put Endpoints
    def do_PUT(self):
        print("Call reached PUT")
        self.execute()

host = ''
port = 3000

# Create and configure the server with the custom request handler
httpd = HTTPServer((host, port), CustomHandler)

print "Server is running on port", port

# Start the server
httpd.serve_forever()
