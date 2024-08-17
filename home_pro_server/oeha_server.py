import json
import os
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

han_host = os.getenv("HAN_API_HOST")
auth_token = os.getenv("SERVER_AUTH_TOKEN")
screen_host = os.getenv('SCREEN_API_HOST')
app_name = os.getenv('APPLICATION_NAME')

class RequestHandler(BaseHTTPRequestHandler):
  # Handle GET requests
  def do_GET(self):
    query = urlparse(self.path).query
    params = dict(qc.split("=") for qc in query.split("&"))

    auth_header = self.headers.get('Authorization')
    if auth_header == None or auth_header != auth_token:
      self.send_response(401)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      return

    if self.path.startswith(f"/get_meter_consumption"):
      # Set response status code
      self.send_response(200)
      # Set headers
      self.send_header("Content-type", "application/json")
      self.end_headers()
      response = request_get_response(f"{han_host}/get_meter_consumption", params)
      if response.ok:
        self.wfile.write(to_response(response, "meter_consump"))
        return

    elif self.path.startswith("/get_meter_status"):
      # Set response status code
      self.send_response(200)
      # Set headers
      self.send_header("Content-type", "application/json")
      self.end_headers()
      response = request_get_response(f"{han_host}/get_meter_status", params)
      if response.ok:
        self.wfile.write(to_response(response, "meter_status"))
        return

    elif self.path.startswith("/get_meter_info"):
      # Set response status code
      self.send_response(200)
      # Set headers
      self.send_header("Content-type", "application/json")
      self.end_headers()
      response = request_get_response(f"{han_host}/get_meter_info", params)
      if response.ok:
        self.wfile.write(to_response(response, "meter_info"))
        return
    else:
      self.send_response(404)
      self.send_header("Content-type", "text/plain")
      self.end_headers()
  
  def do_POST(self):
    auth_header = self.headers.get('Authorization')
    if auth_header == None or auth_header != auth_token:
      self.send_response(401)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      return
    
    if self.path.startswith("/screen"):
      screen_auth_token = os.environ['AUTH_TOKEN']
      if screen_auth_token is None or screen_auth_token == "":
        self.send_response(401)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        output = json.dumps({
          "error": "AUTH_TOKEN not set",
        })
        self.wfile.write(output.encode("utf8"))
        return 
      
      if app_name is None or app_name == "":
        self.send_response(401)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        output = json.dumps({
          "error": "APPLICATION_NAME not set",
        })
        self.wfile.write(output.encode("utf8"))
        return

      headers = {
        "Authorization": f"Basic {screen_auth_token}",
        "Content-Type": "application/json"
      }

      response = requests.get(f"{screen_host}/api/v1/screen/application/{app_name}", headers=headers)
      if not response.ok:
        print("Failed to get screen info")
        self.send_response(400)
        # Set headers
        self.send_header("Content-type", "application/json")
        self.end_headers()
        output = json.dumps({
          "error": "Failed to get screen info",
          "native_response": response.text,
        })
        self.wfile.write(output.encode("utf8"))
        return
      
      # Get first screen
      first_screen = response.json()[0]
      screen_id = first_screen['_id']
      
      screen_url = f"{screen_host}/api/v1/screen/{screen_id}"
      print(f"Calling API (PATCH): {screen_url}")
      data = (self.rfile.read(int(self.headers['content-length']))).decode('utf-8')
      response = requests.patch(screen_url, headers=headers, data=data)
      print(f"Response: {response.text}")
      if not response.ok:
        self.send_response(400)
        # Set headers
        self.send_header("Content-type", "application/json")
        self.end_headers()
        output = json.dumps({
          "error": "Failed to set screen screen info",
          "native_response": response.text,
        })
        self.wfile.write(output.encode("utf8"))
        return
      
      # Set response status code
      self.send_response(200)
      # Set headers
      self.send_header("Content-type", "application/json")
      self.end_headers()
    else:
      self.send_response(404)
      self.send_header("Content-type", "text/plain")
      self.end_headers()

def request_get_response(url, params):
  print(f"Calling API (GET): {url}")
  response = requests.get(url, json=params)
  print(f"Response: {response.text}")
  return response

def to_response(response: requests.Response, result_name: str):
  result = response.json()
  output = json.dumps({
    "Status": result["Status"],
    result_name: json.loads(result[result_name]),
  })
  return output.encode("utf8")

if __name__ == "__main__":
  target_port = 8000
  server_address = ("", target_port)
  httpd = HTTPServer(server_address, RequestHandler)
  print(f"Secure server started on port {target_port}...")
  httpd.serve_forever()