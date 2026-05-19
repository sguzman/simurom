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
    return arr

def main():
    arr1 = key_out_white(Image.open("tmp/base-no-eyes.png"))
    arr2 = np.array(Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA"))
    
    diff = np.abs(arr1.astype(float) - arr2.astype(float))
    print("Diff sum after keying:", diff.sum())
    
if __name__ == "__main__":
    main()
