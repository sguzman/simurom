import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    arr = np.array(img)
    
    # We define a face mask: skin tone region in upper head
    # Skin tone: R > 200, 140 < G < 210, 100 < B < 185
    h, w = arr.shape[:2]
    face_mask = np.zeros((h, w), dtype=bool)
    for y in range(38, 400):
        for x in range(430, 800):
            r, g, b, a = arr[y, x]
            if a > 0:
                if r > 200 and 130 < g < 205 and 100 < b < 185:
                    face_mask[y, x] = True
                    
    # Now let's find dark features inside the face_mask
    # Dark pixels inside face_mask: R < 170, G < 140, B < 120 (lines, eyebrows, nose, mouth)
    features_y, features_x = np.where(
        face_mask &
        (arr[:,:,0] < 180) &
        (arr[:,:,1] < 150) &
        (arr[:,:,2] < 130)
    )
    
    if len(features_y) == 0:
        print("No dark features found on the face skin!")
        return
        
    # Group them using simple distance-based clustering
    coords = np.column_stack((features_x, features_y))
    from sklearn.cluster import DBSCAN
    db = DBSCAN(eps=15, min_samples=3).fit(coords)
    labels = db.labels_
    
    print(f"Found {len(set(labels)) - (1 if -1 in labels else 0)} facial features on the skin:")
    for label in sorted(set(labels)):
        if label == -1:
            continue
        cluster_coords = coords[labels == label]
        min_x, min_y = cluster_coords.min(axis=0)
        max_x, max_y = cluster_coords.max(axis=0)
        avg_x, avg_y = cluster_coords.mean(axis=0)
        print(f"Feature {label}: Y={min_y}:{max_y} (avg {int(avg_y)}), X={min_x}:{max_x} (avg {int(avg_x)}), pixels={len(cluster_coords)}")

if __name__ == "__main__":
    main()
