"""
照片批量压缩工具
用法:
    python compress_photos.py <文件夹或zip路径>
    python compress_photos.py <路径> --width 1600 --quality 75
"""

import argparse
import os
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}


def compress_image(src: Path, dst: Path, max_width: int, quality: int) -> tuple[int, int]:
    """压缩单张图片，返回 (原大小, 新大小) 字节数。"""
    original_size = src.stat().st_size

    with Image.open(src) as img:
        # 根据 EXIF 方向信息修正旋转
        img = ImageOps.exif_transpose(img)

        # 等比缩放
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # PNG 等可能有透明通道，转为 RGB
        if img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # 保存为 JPEG
        dst = dst.with_suffix(".jpg")
        img.save(dst, "JPEG", quality=quality, optimize=True)

    new_size = dst.stat().st_size
    return original_size, new_size


def collect_images(folder: Path) -> list[Path]:
    """递归收集文件夹中的所有图片。"""
    images = []
    for f in sorted(folder.rglob("*")):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(f)
    return images


def main():
    parser = argparse.ArgumentParser(description="照片批量压缩工具")
    parser.add_argument("input", help="文件夹路径 或 .zip 文件路径")
    parser.add_argument("--width", type=int, default=1800, help="最大宽度（默认 1800）")
    parser.add_argument("--quality", type=int, default=80, help="JPEG 质量 1-100（默认 80）")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()

    if not input_path.exists():
        print(f"错误: 路径不存在 - {input_path}")
        sys.exit(1)

    # 确定源文件夹和输出文件夹
    tmp_dir = None
    if input_path.is_file() and input_path.suffix.lower() == ".zip":
        tmp_dir = tempfile.mkdtemp()
        print(f"解压 zip: {input_path.name} ...")
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(tmp_dir)
        src_folder = Path(tmp_dir)
        out_folder = input_path.parent / f"{input_path.stem}_compressed"
    elif input_path.is_dir():
        src_folder = input_path
        out_folder = input_path.parent / f"{input_path.name}_compressed"
    else:
        print("错误: 请提供文件夹路径或 .zip 文件")
        sys.exit(1)

    images = collect_images(src_folder)
    if not images:
        print("未找到任何图片文件")
        sys.exit(0)

    out_folder.mkdir(parents=True, exist_ok=True)
    print(f"找到 {len(images)} 张图片，开始压缩...")
    print(f"参数: 最大宽度={args.width}px, quality={args.quality}")
    print(f"输出: {out_folder}\n")

    total_original = 0
    total_new = 0

    for i, img_path in enumerate(images, 1):
        rel = img_path.relative_to(src_folder)
        dst_path = out_folder / rel
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            orig, new = compress_image(img_path, dst_path, args.width, args.quality)
            total_original += orig
            total_new += new
            ratio = (1 - new / orig) * 100 if orig > 0 else 0
            print(f"  [{i}/{len(images)}] {rel.name}: {orig/1024:.0f}KB -> {new/1024:.0f}KB  (-{ratio:.0f}%)")
        except Exception as e:
            print(f"  [{i}/{len(images)}] {rel.name}: 跳过 ({e})")

    # 清理临时目录
    if tmp_dir:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"\n完成! 总计: {total_original/1024/1024:.1f}MB -> {total_new/1024/1024:.1f}MB  "
          f"(-{(1 - total_new/total_original)*100:.0f}%)" if total_original > 0 else "\n完成!")


if __name__ == "__main__":
    main()
