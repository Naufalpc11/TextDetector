# Machine Learning - YOLO MNIST Classification

Project ini melatih model YOLO klasifikasi digit (0-9) dengan preprocessing otomatis sebelum training.

## 1) Prasyarat

- Python 3.10 atau lebih baru
- pip
- Windows PowerShell (sesuai environment kamu saat ini)

## 2) Install dependency

Jalankan dari folder machine-learning.

```powershell
cd "D:\Semester 6\Deep Learning\TextEditor\machine-learning"
```

Kalau virtual environment belum ada:

```powershell
python -m venv .venv
```

Aktifkan virtual environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& ".\.venv\Scripts\Activate.ps1"
```

Install package:

```powershell
pip install -r requirements.txt
```

## 3) Struktur dataset yang didukung

Script training mendukung salah satu dari 2 format ini:

### Format A (langsung)

- dataset/mnist_png/train/0 sampai 9
- dataset/mnist_png/val/0 sampai 9

### Format B (alternatif)

- dataset/mnist_png/trainingSet/trainingSet/0 sampai 9
- dataset/mnist_png/trainingSample/trainingSample/0 sampai 9

Jika format B dipakai, script akan otomatis membuat versi siap-train di folder _prepared_cls.

## 4) Cara run training

```powershell
python train.py
```

Yang terjadi saat training:

- Validasi kelas train dan val harus lengkap (0-9)
- Preprocessing gambar otomatis:
  - grayscale
  - autocontrast
  - resize/pad ke 32x32
  - konversi ke RGB
- Hasil preprocessing disimpan ke folder cache:
  - dataset/mnist_png/_preprocessed_cls_32
- Model kemudian dilatih memakai dataset hasil preprocessing tersebut

## 5) Lokasi hasil training

Hasil umumnya tersimpan di:

- runs/classify/train/weights/best.pt
- runs/classify/train/weights/last.pt

Jika nama folder train sudah ada, YOLO bisa membuat train-2, train-3, dst.

## 6) Menjalankan API (opsional)

Setelah ada model best.pt, kamu bisa jalankan API FastAPI:

```powershell
uvicorn main:app --reload
```

Lalu akses:

- http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## 7) Troubleshooting singkat

- Error MODEL_PATH tidak ditemukan:
  - Pastikan training sudah jalan minimal 1x agar best.pt terbentuk.
- Error struktur dataset tidak dikenali:
  - Cek kembali susunan folder train/val atau trainingSet/trainingSample.
- Training lambat:
  - Saat ini device di train.py diset ke CPU. Jika ada GPU NVIDIA, bisa ubah parameter device menjadi 0.
