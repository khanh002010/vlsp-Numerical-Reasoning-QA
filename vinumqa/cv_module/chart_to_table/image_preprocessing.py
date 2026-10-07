"""Preserve native image dimensions below the area cap; never stretch to a fixed size."""
from PIL import Image

MAX_PIXELS = 1_400_000


def preprocess_image(image, max_pixels=MAX_PIXELS):
    if max_pixels <= 0:
        raise ValueError("max_pixels must be positive")
    width, height = image.size
    if width * height <= max_pixels:
        return image
    scale = (max_pixels / (width * height)) ** 0.5
    return image.resize((max(1, int(width * scale)), max(1, int(height * scale))),
                        Image.Resampling.LANCZOS)
