import numpy as np
from PIL import Image
from collections import deque

def key_out_white(img):
    arr = np.array(img.convert("RGBA"))
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
                
    while queue:
        cx, cy = queue.popleft()
        arr[cy, cx, 3] = 0
        
        for nx, ny in [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]:
            if 0 <= nx < w and 0 <= ny < h:
                if not visited[ny, nx]:
                    if arr[ny, nx, 0] > 240 and arr[ny, nx, 1] > 240 and arr[ny, nx, 2] > 240:
                        visited[ny, nx] = True
                        queue.append((nx, ny))
    return Image.fromarray(arr)

def main():
    base = Image.open("tmp/base.png").convert("RGBA")
    brows = Image.open("tmp/eye-brows.png").convert("RGBA")
    
    base_keyed = key_out_white(base)
    brows_keyed = key_out_white(brows)
    
    # Overlay eyebrows directly onto base
    composite = Image.alpha_composite(base_keyed, brows_keyed)
    composite.save("scratch/preview_brows.png")
    print("Saved keyed composite to scratch/preview_brows.png")

if __name__ == "__main__":
    main()
