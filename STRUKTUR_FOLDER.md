# Struktur Folder - MNIST Digit Classifier

Proyek ini telah diorganisir dengan pemisahan yang jelas antara backend dan frontend.

## 📁 Struktur Direktori

```
d:\Semester 6\Deep Learning\TextEditor\
│
├── backend/                          # Backend FastAPI + YOLO Model
│   ├── main.py                       # FastAPI server
│   ├── train.py                      # Training script
│   ├── api_models.py                 # Model definitions
│   ├── requirements.txt               # Python dependencies
│   ├── yolo11n-cls.pt                # Pretrained YOLO model
│   └── __pycache__/
│
├── frontend/                          # Frontend Vue.js + Vite
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── components/
│   │   │   └── DigitClassifier.vue   # Main UI component
│   │   └── assets/
│   ├── public/
│   ├── package.json                   # Node dependencies
│   ├── vite.config.ts                 # Vite configuration
│   ├── tsconfig.json                  # TypeScript config
│   └── node_modules/
│
├── dataset/                           # MNIST Dataset
│   └── mnist_png/
│       ├── _prepared_cls/
│       ├── _preprocessed_cls_32/
│       ├── trainingSample/
│       ├── trainingSet/
│       └── ...
│
├── runs/                              # Training outputs
│   └── classify/
│       └── train/
│           ├── weights/
│           │   ├── best.pt            # Best trained model
│           │   └── last.pt
│           └── results.csv
│
# FOLDER LAMA (masih tersimpan)
├── machine-learning/                  # ⚠️ Original backend folder (deprecated)
├── web-application/                   # ⚠️ Original frontend folder (deprecated)
│
└── README.md

```

## 🚀 Cara Menjalankan

### 1️⃣ Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server akan berjalan di **http://localhost:8000**

**Endpoint utama:**
- `GET http://localhost:8000/` - Health check
- `POST http://localhost:8000/tebak-angka` - Klasifikasi digit

### 2️⃣ Frontend (Vue.js)

Buka terminal terpisah:

```bash
cd frontend
npm install
npm run dev
```

Aplikasi akan berjalan di **http://localhost:5175** (atau port berikutnya jika sudah digunakan)

## 📝 Catatan Penting

- ✅ **Folder lama** (`machine-learning/`, `web-application/`) masih tersimpan untuk referensi
- ✅ **Backend** otomatis mencari model di `../runs/classify/train/weights/best.pt`
- ✅ **Frontend** berkomunikasi dengan backend di `http://localhost:8000`
- ⚠️ Pastikan **backend berjalan dulu** sebelum membuka frontend

## 🔄 Workflow Development

1. **Train Model** (satu kali atau saat update dataset):
   ```bash
   cd backend
   python train.py
   ```

2. **Jalankan Backend**:
   ```bash
   cd backend
   python main.py
   ```

3. **Jalankan Frontend** (di terminal baru):
   ```bash
   cd frontend
   npm run dev
   ```

4. **Buka browser** dan akses aplikasi

## 📦 Dependencies

### Backend
- `fastapi` - Web framework
- `ultralytics` - YOLO model
- `pillow` - Image processing
- `uvicorn` - ASGI server
- `torch` - PyTorch

### Frontend
- `vue` - UI framework
- `vite` - Build tool
- `typescript` - Type safety
- `axios` - HTTP client

## 🎯 Struktur File Baru vs Lama

| Komponen | Lama | Baru |
|----------|------|------|
| Backend | `machine-learning/` | `backend/` |
| Frontend | `web-application/text-classificaiton-fe/` | `frontend/` |
| Training | `machine-learning/train.py` | `backend/train.py` |
| Server | `machine-learning/main.py` | `backend/main.py` |
| UI | `web-application/text-classificaiton-fe/` | `frontend/` |

---

✨ **Struktur baru lebih clean dan lebih mudah untuk scaling!**
