import requests
from pathlib import Path

FACE_ENDPOINT = "https://facemariogimnasio.cognitiveservices.azure.com/"
FACE_KEY = "BNRkVttmRtnOSAKYiwvvTedjftbM38ZRoAVxcermC7NX3HPWxCgzJQQJ99CAAC5RqLJXJ3w3AAAKACOG70xU"
PERSON_GROUP_ID = "gym-demo4"

# Detect
detect_url = f"{FACE_ENDPOINT}/face/v1.2/detect"
img = Path("test.jpg").read_bytes()
r = requests.post(
    detect_url,
    params={"returnFaceId": "true", "recognitionModel": "recognition_04"},
    headers={"Ocp-Apim-Subscription-Key": FACE_KEY, "Content-Type": "application/octet-stream"},
    data=img,
    timeout=15
)
print("DETECT:", r.status_code, r.text)
r.raise_for_status()
face_id = r.json()[0]["faceId"]

# Identify
identify_url = f"{FACE_ENDPOINT}/face/v1.2/identify"
payload = {"personGroupId": PERSON_GROUP_ID, "faceIds": [face_id], "maxNumOfCandidatesReturned": 1, "confidenceThreshold": 0.6}
r2 = requests.post(
    identify_url,
    headers={"Ocp-Apim-Subscription-Key": FACE_KEY, "Content-Type": "application/json"},
    json=payload,
    timeout=15
)
print("IDENTIFY:", r2.status_code, r2.text)
r2.raise_for_status()
