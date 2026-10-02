#!/usr/bin/env python3
import sys
import os
import cv2
import numpy as np
from PIL import Image
from rembg import remove

def prep_photo(input_path="source-photo.jpg", output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        sys.exit(1)

    print(f"1. Loading image {input_path}...")
    img_pil = Image.open(input_path)

    # Convert to RGB if needed
    if img_pil.mode != "RGB":
        img_pil = img_pil.convert("RGB")

    # Resize if too large to speed up processing
    max_dim = 1000
    if max(img_pil.size) > max_dim:
        img_pil.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    print("2. Removing background with rembg...")
    no_bg = remove(img_pil)

    # Convert to numpy array
    rgba = np.array(no_bg)
    alpha = rgba[:, :, 3]
    rgb = rgba[:, :, :3]

    print("3. Converting to grayscale and applying CLAHE contrast...")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Adaptive histogram equalization (CLAHE) to bring out details and shadows
    clahe = cv2.createCLAHE(clipLimit=2.8, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    print("4. Compositing over pure white background...")
    # Composite: where alpha=0 -> 255 (white), where alpha=255 -> enhanced
    alpha_norm = (alpha.astype(np.float32) / 255.0)
    # Background cut-off to eliminate edge halos
    alpha_norm[alpha_norm < 0.25] = 0.0
    
    white_bg = np.ones_like(enhanced, dtype=np.float32) * 255.0
    composited = (enhanced.astype(np.float32) * alpha_norm + white_bg * (1.0 - alpha_norm)).astype(np.uint8)

    # Push near-white highlights to pure white so they become clean spaces
    composited[composited > 235] = 255

    out_pil = Image.fromarray(composited)
    out_pil.save(output_path)
    print(f"Saved prepped photo to {output_path} ({out_pil.size[0]}x{out_pil.size[1]})")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    prep_photo(src)
