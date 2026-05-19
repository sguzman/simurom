import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    arr = np.array(img)
    
    # We restrict to the face/head area: Y in [38, 300], X in [520, 700]
    face_region = arr[38:300, 520:700]
    # Let's find dark pixels (like eyebrows, nose, mouth) in the face region
    # Dark pixels have low R, G, B (e.g., R < 100, G < 100, B < 100) and A > 0
    dark_y, dark_x = np.where(
        (face_region[:,:,0] < 120) &
        (face_region[:,:,1] < 120) &
        (face_region[:,:,2] < 120) &
        (face_region[:,:,3] > 0)
    )
    
    # Let's map back to actual coordinates in blonde_base.png
    actual_dark_y = dark_y + 38
    actual_dark_x = dark_x + 520
    
    # Group dark pixels by Y coordinates to find horizontal lines (like eyebrows, nose, mouth)
    # Let's count how many dark pixels are at each Y coordinate
    y_counts = np.bincount(actual_dark_y)
    
    print("Dark pixel horizontal concentrations on the face (possible features):")
    for y_idx in np.argwhere(y_counts > 10).flatten():
        # Get average X for this Y
        avg_x = int(np.mean(actual_dark_x[actual_dark_y == y_idx]))
        # Check width span of dark pixels at this Y
        xs_at_y = actual_dark_x[actual_dark_y == y_idx]
        span_x = xs_at_y.max() - xs_at_y.min() + 1
        print(f"Y={y_idx}: count={y_counts[y_idx]}, avg_x={avg_x}, span_x={span_x} (X: {xs_at_y.min()} to {xs_at_y.max()})")

if __name__ == "__main__":
    main()
