from ultralytics import YOLO
from pathlib import Path
import os
import shutil
from PIL import Image, ImageOps


PREPROCESS_VERSION = "v1"
TARGET_IMAGE_SIZE = 32


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


def preprocess_single_image(src_path: Path, dst_path: Path) -> bool:
    try:
        with Image.open(src_path) as image:
            # Standardisasi kontras dan ukuran agar distribusi input lebih konsisten.
            image = ImageOps.grayscale(image)
            image = ImageOps.autocontrast(image, cutoff=1)
            image = ImageOps.pad(
                image,
                (TARGET_IMAGE_SIZE, TARGET_IMAGE_SIZE),
                method=Image.Resampling.BICUBIC,
                color=0,
                centering=(0.5, 0.5),
            )
            image = image.convert("RGB")
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(dst_path, format="PNG", optimize=True)
        return True
    except Exception:
        return False


def build_preprocessed_dataset(dataset_root: Path) -> Path:
    output_root = dataset_root.parent / f"_preprocessed_cls_{TARGET_IMAGE_SIZE}"
    marker_file = output_root / f".{PREPROCESS_VERSION}.done"

    if marker_file.exists():
        print(f"Preprocessing: cache ditemukan, skip proses ulang di {output_root}")
        return output_root

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    image_tasks: list[tuple[Path, Path]] = []
    for split in ("train", "val"):
        split_dir = dataset_root / split
        if not split_dir.is_dir():
            continue
        for class_dir in sorted([p for p in split_dir.iterdir() if p.is_dir()]):
            for src_path in class_dir.iterdir():
                if not src_path.is_file():
                    continue
                if src_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
                    continue
                dst_path = output_root / split / class_dir.name / f"{src_path.stem}.png"
                image_tasks.append((src_path, dst_path))

    total_candidates = len(image_tasks)
    if total_candidates == 0:
        raise ValueError("Tidak ada gambar yang ditemukan untuk preprocessing.")

    print(f"Preprocessing: mulai memproses {total_candidates} gambar...")

    total_images = 0
    failed_images = 0
    progress_step = max(1, total_candidates // 10)
    for index, (src_path, dst_path) in enumerate(image_tasks, start=1):
        total_images += 1
        if not preprocess_single_image(src_path, dst_path):
            failed_images += 1

        if index == total_candidates or index % progress_step == 0:
            progress_percent = (index / total_candidates) * 100
            print(
                f"Preprocessing progress: {index}/{total_candidates} "
                f"({progress_percent:.0f}%)"
            )

    if failed_images > 0:
        raise ValueError(
            f"Preprocessing gagal pada {failed_images} dari {total_images} gambar."
        )

    marker_file.write_text(
        f"preprocess_version={PREPROCESS_VERSION}\n"
        f"image_size={TARGET_IMAGE_SIZE}\n"
        f"images={total_images}\n",
        encoding="utf-8",
    )
    print("Preprocessing selesai dan cache berhasil dibuat.")
    return output_root


def main():
    raw_dataset_root = Path("../dataset/mnist_png")
    dataset_root = prepare_dataset_root(raw_dataset_root)
    validate_dataset(dataset_root)
    preprocessed_root = build_preprocessed_dataset(dataset_root)

    # Memuat model YOLO versi klasifikasi yang paling ringan
    # Catatan: Jika error karena versi 12 belum stabil, ubah menjadi "yolov8n-cls.pt"
    model = YOLO("yolo11n-cls.pt")  

    print("Memulai proses training AI...")
    
    # Mulai training
    results = model.train(
        data=str(preprocessed_root),
        epochs=20,             # Tambah epoch agar model sempat konvergen
        imgsz=TARGET_IMAGE_SIZE,
        batch=128,
        patience=8,
        optimizer="AdamW",
        lr0=0.002,
        weight_decay=0.0005,
        cos_lr=True,
        augment=True,
        fliplr=0.0,            # Flip kiri-kanan kurang cocok untuk digit
        flipud=0.0,
        degrees=8.0,
        translate=0.08,
        scale=0.15,
        erasing=0.1,
        device="cpu",
        exist_ok=True
    )

    print(f"Dataset original: {dataset_root}")
    print(f"Dataset preprocessing: {preprocessed_root}")
    print(f"Training selesai. Folder hasil: {results.save_dir}")
    print("Model terbaik ada di <save_dir>/weights/best.pt")

if __name__ == '__main__':
    main()
