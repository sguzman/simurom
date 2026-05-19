#!/usr/bin/env python3
import glob
import numpy as np
from PIL import Image
from collections import deque

def process_image(img_path):
    print(f"Processing {img_path}...")
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    queue = deque()
    
    # Corners
    corners = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
    for cx, cy in corners:
        if arr[cy, cx, 0] > 240 and arr[cy, cx, 1] > 240 and arr[cy, cx, 2] > 240:
            if not visited[cy, cx]:
                visited[cy, cx] = True
                queue.append((cx, cy))
                
    count = 0
    while queue:
        cx, cy = queue.popleft()
        arr[cy, cx, 3] = 0
        count += 1
        
        for nx, ny in [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]:
            if 0 <= nx < w and 0 <= ny < h:
                if not visited[ny, nx]:
                    if arr[ny, nx, 0] > 240 and arr[ny, nx, 1] > 240 and arr[ny, nx, 2] > 240:
                        visited[ny, nx] = True
                        queue.append((nx, ny))
                        
    print(f"-> Keyed out {count} background pixels out of {w*h} total.")
    Image.fromarray(arr).save(img_path, "PNG")

def main():
    files = glob.glob("assets/mini_game/images/blonde_*.png")
    for f in files:
        process_image(f)

if __name__ == "__main__":
    main()
