import requests
import base64
from pathlib import Path
import json  # Para mejor manejo de errores

# TU URL de Logic App
LA_URL = "https://prod-04.swedencentral.logic.azure.com:443/workflows/9a6c42b13c4542b788b1dc28da3372b5/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=tigD71zv5RnExEPr1uiQYDXaXx1P85nlQqT9Gy24bv4"

foto_path = Path("test.jpg")
foto_bytes = foto_path.read_bytes()          # bytes reales del JPG
foto_b64 = base64.b64encode(foto_bytes).decode("ascii")  # los conviertes a texto base64

payload = {"foto": foto_b64}
headers = {"Content-Type": "application/json"}

r = requests.post(LA_URL, json=payload, headers=headers, timeout=60)
print("STATUS:", r.status_code)
print("BODY:", r.text)
