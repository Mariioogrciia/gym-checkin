import requests
from pathlib import Path
import time

# =========================
# CONFIG
# =========================
FACE_ENDPOINT = "https://facemariogimnasio.cognitiveservices.azure.com/"
FACE_KEY = "BNRkVttmRtnOSAKYiwvvTedjftbM38ZRoAVxcermC7NX3HPWxCgzJQQJ99CAAC5RqLJXJ3w3AAAKACOG70xU"

API_VER = "v1.2"
PERSON_GROUP_ID = "gym-demo4"   # cambia a gym-demo si quieres, pero mejor nuevo para ir limpio
RECO_MODEL = "recognition_04"

# Tus carpetas reales (según tu captura): PROYECTO/face/messi y PROYECTO/face/luuk
BASE_DIR = Path(__file__).resolve().parent
MESSI_DIR = BASE_DIR / "face" / "messi"
LUUK_DIR  = BASE_DIR / "face" / "luuk"

# =========================
# HTTP helpers
# =========================
def _h_json():
    return {
        "Ocp-Apim-Subscription-Key": FACE_KEY,
        "Content-Type": "application/json"
    }

def _h_octet():
    return {
        "Ocp-Apim-Subscription-Key": FACE_KEY,
        "Content-Type": "application/octet-stream"
    }

def _h_key():
    return {"Ocp-Apim-Subscription-Key": FACE_KEY}

def create_group():
    url = f"{FACE_ENDPOINT}/face/{API_VER}/persongroups/{PERSON_GROUP_ID}"
    body = {"name": "Gimnasio demo", "userData": "demo clase", "recognitionModel": RECO_MODEL}
    r = requests.put(url, headers=_h_json(), json=body, timeout=30)
    r.raise_for_status()

def create_person(name: str) -> str:
    url = f"{FACE_ENDPOINT}/face/{API_VER}/persongroups/{PERSON_GROUP_ID}/persons"
    r = requests.post(url, headers=_h_json(), json={"name": name}, timeout=30)
    r.raise_for_status()
    return r.json()["personId"]

def add_face(person_id: str, img_path: Path):
    url = f"{FACE_ENDPOINT}/face/{API_VER}/persongroups/{PERSON_GROUP_ID}/persons/{person_id}/persistedfaces"
    r = requests.post(url, headers=_h_octet(), data=img_path.read_bytes(), timeout=30)

    if r.status_code >= 400:
        # imprime el motivo exacto del 400 (No face / More than 1 face / InvalidImage...)
        print(f"❌ ERROR subiendo {img_path.name} -> {r.status_code} {r.text}")
        return False

    return True


def train_group():
    url = f"{FACE_ENDPOINT}/face/{API_VER}/persongroups/{PERSON_GROUP_ID}/train"
    r = requests.post(url, headers=_h_key(), timeout=30)
    r.raise_for_status()

def get_training_status():
    url = f"{FACE_ENDPOINT}/face/{API_VER}/persongroups/{PERSON_GROUP_ID}/training"
    r = requests.get(url, headers=_h_key(), timeout=30)
    r.raise_for_status()
    return r.json()

def wait_training(max_seconds=60):
    t0 = time.time()
    while True:
        st = get_training_status()
        status = st.get("status")
        print("Training status:", st)
        if status in ("succeeded", "failed"):
            return st
        if time.time() - t0 > max_seconds:
            return st
        time.sleep(2)

# =========================
# MAIN
# =========================
def list_images(folder: Path):
    imgs = list(folder.glob("*.jpg")) + list(folder.glob("*.JPG")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.JPEG"))
    return imgs

def main():
    if not MESSI_DIR.exists():
        raise SystemExit(f"No existe la carpeta: {MESSI_DIR}")
    if not LUUK_DIR.exists():
        raise SystemExit(f"No existe la carpeta: {LUUK_DIR}")

    messi_imgs = list_images(MESSI_DIR)
    luuk_imgs = list_images(LUUK_DIR)

    print(f"Carpeta Messi: {MESSI_DIR} -> {len(messi_imgs)} fotos")
    print(f"Carpeta Luuk : {LUUK_DIR} -> {len(luuk_imgs)} fotos")

    if len(messi_imgs) == 0 or len(luuk_imgs) == 0:
        raise SystemExit("No se encontraron fotos (revisa que sean .jpg/.jpeg y estén en esas carpetas).")

    # 1) Crear grupo
    create_group()  # Create Person Group [web:112]
    print("OK PersonGroup creado:", PERSON_GROUP_ID)

    # 2) Crear personas
    messi_id = create_person("Messi")
    luuk_id = create_person("Luuk de Jong")
    print("PERSONID_MESSI:", messi_id)
    print("PERSONID_LUUK :", luuk_id)

    # 3) Subir fotos
    for p in messi_imgs:
        add_face(messi_id, p)  # Add face (octet-stream) [web:67]
    print("OK fotos Messi subidas:", len(messi_imgs))

    for p in luuk_imgs:
        add_face(luuk_id, p)   # Add face (octet-stream) [web:67]
    print("OK fotos Luuk subidas:", len(luuk_imgs))

    # 4) Entrenar
    train_group()  # Train (crucial) [web:166]
    print("Train lanzado")

    # 5) Esperar estado
    final_status = wait_training(max_seconds=90)  # Training status endpoint [web:167]
    if final_status.get("status") != "succeeded":
        raise SystemExit(f"Training NO OK: {final_status}")

    print("✅ Training succeeded")
    print("Siguiente: guarda estos personId en SQL (FacePersons).")

if __name__ == "__main__":
    main()
