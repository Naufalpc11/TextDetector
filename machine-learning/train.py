from ultralytics import YOLO
from pathlib import Path
import os
import shutil


def ensure_dir_link_or_copy(src: Path, dst: Path) -> None:
    if dst.exists():
        return
    try:
        os.symlink(src.resolve(), dst, target_is_directory=True)
    except OSError:
        shutil.copytree(src, dst)


def prepare_dataset_root(dataset_root: Path) -> Path:
    if (dataset_root / "train").is_dir() and (dataset_root / "val").is_dir():
        return dataset_root

    alt_train = dataset_root / "trainingSet" / "trainingSet"
    alt_val = dataset_root / "trainingSample" / "trainingSample"
    if alt_train.is_dir() and alt_val.is_dir():
        prepared_root = dataset_root / "_prepared_cls"
        prepared_root.mkdir(parents=True, exist_ok=True)
        ensure_dir_link_or_copy(alt_train, prepared_root / "train")
        ensure_dir_link_or_copy(alt_val, prepared_root / "val")
        return prepared_root

    raise FileNotFoundError(
        "Struktur dataset tidak dikenali. "
        "Harus ada `train/val` atau `trainingSet/trainingSet` + `trainingSample/trainingSample`."
    )


def validate_dataset(dataset_root: Path) -> None:
    expected_classes = {str(i) for i in range(10)}
    train_dir = dataset_root / "train"
    val_dir = dataset_root / "val"

    train_classes = {p.name for p in train_dir.iterdir() if p.is_dir()}
    val_classes = {p.name for p in val_dir.iterdir() if p.is_dir()}

    missing_train = sorted(expected_classes - train_classes, key=int)
    missing_val = sorted(expected_classes - val_classes, key=int)

    if missing_train or missing_val:
        raise ValueError(
            "Dataset tidak lengkap. "
            f"train kurang kelas: {missing_train or 'tidak ada'}, "
            f"val kurang kelas: {missing_val or 'tidak ada'}."
        )

def main():
    raw_dataset_root = Path("./dataset/mnist_png")
    dataset_root = prepare_dataset_root(raw_dataset_root)
    validate_dataset(dataset_root)

    # Memuat model YOLO versi klasifikasi yang paling ringan
    # Catatan: Jika error karena versi 12 belum stabil, ubah menjadi "yolov8n-cls.pt"
    model = YOLO("yolo11n-cls.pt")  

    print("Memulai proses training AI...")
    
    # Mulai training
    # PENTING: Pastikan parameter 'data' sama persis dengan nama folder dataset gambarmu!
    results = model.train(
        data=str(dataset_root),
        epochs=10,             # Belajar mengulang dataset 10 kali
        imgsz=32,              # Ukuran gambar diubah ke 32x32 pixel
        device="cpu",          # Hapus baris ini atau ubah jadi "0" kalau laptopmu pakai GPU NVIDIA
        exist_ok=True
    )

    print(f"Dataset yang dipakai: {dataset_root}")
    print(f"Training selesai. Folder hasil: {results.save_dir}")
    print("Model terbaik ada di <save_dir>/weights/best.pt")

if __name__ == '__main__':
    main()
