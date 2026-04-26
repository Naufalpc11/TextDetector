from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image, ImageOps, ImageStat
import io
import os
from pathlib import Path

TARGET_IMAGE_SIZE = 32

app = FastAPI()

# Mencegah error CORS saat Vue (port 5173) mencoba nembak API Python (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def resolve_model_path() -> Path:
    env_model_path = os.getenv("MODEL_PATH")
    if env_model_path:
        candidate = Path(env_model_path)
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"MODEL_PATH tidak ditemukan: {candidate}")

    stable_path = Path("runs/classify/train/weights/best.pt")
    if stable_path.exists():
        return stable_path

    candidates = sorted(
        [
            p for p in Path("runs").rglob("weights/best.pt")
            if "classify" in p.parts
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if candidates:
        return candidates[0]

    raise FileNotFoundError(
        "Model best.pt belum ada. Jalankan `python train.py` dulu."
    )


model_path = resolve_model_path()
model = YOLO(str(model_path))


def preprocess_for_inference(image: Image.Image) -> tuple[Image.Image, bool]:
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=1)

    # Jika background dominan terang (mis. screenshot Notepad), balik agar mirip MNIST.
    mean_intensity = ImageStat.Stat(gray).mean[0]
    inverted = mean_intensity > 127
    if inverted:
        gray = ImageOps.invert(gray)

    # Fokus ke area tulisan agar digit lebih centered.
    bw = gray.point(lambda p: 255 if p > 40 else 0)
    bbox = bw.getbbox()
    if bbox:
        gray = gray.crop(bbox)

    gray = ImageOps.pad(
        gray,
        (TARGET_IMAGE_SIZE, TARGET_IMAGE_SIZE),
        method=Image.Resampling.BICUBIC,
        color=0,
        centering=(0.5, 0.5),
    )
    return gray.convert("RGB"), inverted

@app.get("/")
def read_root():
    return {
        "pesan": "API Machine Learning Aktif!",
        "model_path": str(model_path),
        "jumlah_kelas": len(model.names),
        "kelas": list(model.names.values())
    }

@app.post("/tebak-angka")
async def tebak_angka(file: UploadFile = File(...)):
    try:
        # 1. Baca gambar yang dikirim dari Vue
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image, was_inverted = preprocess_for_inference(image)

        # 2. Suruh YOLO menebak gambar tersebut
        results = model(image)
        
        # 3. Ekstrak hasil tebakan (probabilitas tertinggi)
        probs = results[0].probs
        tebakan = results[0].names[probs.top1]
        keyakinan = float(probs.top1conf) * 100

        # 4. Kembalikan respons ke Vue
        return {
            "status": "sukses",
            "angka": tebakan,
            "persentase_keyakinan": f"{keyakinan:.2f}%",
            "preprocessing": {
                "auto_invert": was_inverted,
                "target_size": TARGET_IMAGE_SIZE,
            },
        }
    except Exception as e:
        return {"status": "error", "pesan": str(e)}
