import json
import os
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

han_host = os.getenv("HAN_API_HOST")
auth_token = os.getenv("SERVER_AUTH_TOKEN")

class RequestHandler(BaseHTTPRequestHandler):
  # Handle GET requests
  def do_GET(self):
    query = urlparse(self.path).query
    params = dict(qc.split("=") for qc in query.split("&"))

    auth_header = self.headers.getheader('Authorization')
    if auth_header == None or auth_header != auth_token:
      self.send_response(401)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      return

    if self.path.startswith("/get_meter_consumption"):
      # Set response status code
      self.send_response(200)
      # Set headers
      self.send_header("Content-type", "application/json")
      self.end_headers()
      response = request_get_response("get_meter_consumption", params)
      if response.ok:
        self.wfile.write(to_response(response, "meter_consump"))
        return

    elif self.path.startswith("/get_meter_status"):
      # Set response status code
      self.send_response(200)
      # Set headers
      self.send_header("Content-type", "application/json")
      self.end_headers()
      response = request_get_response("get_meter_status", params)
      if response.ok:
        self.wfile.write(to_response(response, "meter_status"))
        return

    elif self.path.startswith("/get_meter_info"):
      # Set response status code
      self.send_response(200)
      # Set headers
      self.send_header("Content-type", "application/json")
      self.end_headers()
      response = request_get_response("get_meter_info", params)
      if response.ok:
        self.wfile.write(to_response(response, "meter_info"))
        return
    else:
      self.send_response(404)
      self.send_header("Content-type", "text/plain")
      self.end_headers()

def request_get_response(api, params):
  print(f"Calling API: {api}")
  url = f"{han_host}/" + f"{api}"
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
  server_address = ("", 8000)
  httpd = HTTPServer(server_address, RequestHandler)
  print("Secure server started on port 8000...")
  httpd.serve_forever()