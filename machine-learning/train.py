from ultralytics import YOLO

def main():
    # Memuat model YOLO versi klasifikasi yang paling ringan
    # Catatan: Jika error karena versi 12 belum stabil, ubah menjadi "yolov8n-cls.pt"
    model = YOLO("yolo11n-cls.pt")  

    print("Memulai proses training AI...")
    
    # Mulai training
    # PENTING: Pastikan parameter 'data' sama persis dengan nama folder dataset gambarmu!
    results = model.train(
        data="./dataset/mnist_png", 
        epochs=10,            # Belajar mengulang dataset 10 kali
        imgsz=32,             # Ukuran gambar diubah ke 32x32 pixel
        device="cpu"          # Hapus baris ini atau ubah jadi "0" kalau laptopmu pakai GPU NVIDIA
    )
    
    print("Training Selesai! Model terbaikmu ada di folder runs/classify/train/weights/best.pt")

if __name__ == '__main__':
    main()