# compress-photos

批量压缩照片的命令行工具。缩小分辨率 + 降低 JPEG 质量，适合作业、文档插图等不需要原图画质的场景。

## 环境要求

- Python 3.10+
- Pillow

```bash
pip install Pillow
```

## 使用方法

```bash
# 压缩文件夹中的所有照片
python compress_photos.py C:\Users\你的照片文件夹

# 压缩 zip 文件
python compress_photos.py C:\Users\photos.zip

# 自定义最大宽度和质量
python compress_photos.py C:\Users\照片 --width 1600 --quality 75
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `input` | (必填) | 文件夹路径 或 `.zip` 文件路径 |
| `--width` | 1800 | 最大宽度（px），超过则等比缩放 |
| `--quality` | 80 | JPEG 压缩质量（1-100） |

## 输出

- 压缩后的照片保存在输入路径旁边的 `{输入名}_compressed` 文件夹中
- 原始文件不会被修改
- 所有格式（jpg/png/bmp/webp/tiff）统一输出为 JPEG
- 自动修正手机拍照的 EXIF 旋转方向

## 示例输出

```
找到 16 张图片，开始压缩...
参数: 最大宽度=1800px, quality=80
输出: D:\Downloads\photos_compressed

  [1/16] IMG_001.jpg: 4874KB -> 1056KB  (-78%)
  [2/16] IMG_002.jpg: 5555KB -> 1181KB  (-79%)
  ...

完成! 总计: 59.4MB -> 11.1MB  (-81%)
```
