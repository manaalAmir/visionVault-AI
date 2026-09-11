import os
import pickle
import faiss
import numpy as np
from embedding import get_image_embedding

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER=os.path.join(BASE_DIR,"..","images")
INDEX_FILE=os.path.join(BASE_DIR,"..","vectors","image_index.faiss")
NAMES_FILE=os.path.join(BASE_DIR,"..","vectors","image_names.pkl")
SAVE_EVERY=500
os.makedirs(os.path.join(BASE_DIR,"..","vectors"),exist_ok=True)

if os.path.exists(INDEX_FILE) and os.path.exists(NAMES_FILE):
    print("Loading existing database...")
    index=faiss.read_index(INDEX_FILE)
    with open(NAMES_FILE,"rb") as f:
        image_names=pickle.load(f)
    print(f"Existing images:{len(image_names)}")
else:
    print("Creating new database...")
    image_names=[]
    dimension=512
    index=faiss.IndexHNSWFlat(dimension,32,faiss.METRIC_INNER_PRODUCT)
    index.hnsw.efConstruction=200

valid_extensions=(".jpg",".jpeg",".png",".webp",".jfif")
all_images=[]
for filename in os.listdir(IMAGE_FOLDER):
    if filename.lower().endswith(valid_extensions):
        if filename not in image_names:
            all_images.append(filename)

total=len(all_images)
print(f"\nNew images to index:{total}")
if total==0:
    print("Everything is already indexed.")
    exit()

new_vectors=[]
for count,filename in enumerate(all_images,start=1):
    print(f"Processing {count}/{total}:{filename}")
    image_path=os.path.join(IMAGE_FOLDER,filename)
    try:
        embedding=get_image_embedding(image_path)
    except Exception as e:
        print(f"Skipping {filename},error:{e}")
        continue

    new_vectors.append(embedding[0])
    image_names.append(filename)
    if count%SAVE_EVERY==0:
        vectors=np.array(new_vectors).astype("float32")
        faiss.normalize_L2(vectors)
        index.add(vectors)
        faiss.write_index(index,INDEX_FILE)
        with open(NAMES_FILE,"wb") as f:
            pickle.dump(image_names,f)
        print(f"\nCheckpoint saved({count}/{total})")
        new_vectors=[]
if len(new_vectors)>0:
    vectors=np.array(new_vectors).astype("float32")
    faiss.normalize_L2(vectors)
    index.add(vectors)

faiss.write_index(index,INDEX_FILE)
with open(NAMES_FILE,"wb") as f:
    pickle.dump(image_names,f)

print("\nIndexing complete!")
print(f"Total indexed images: {len(image_names)}")
print(f"Vectors stored: {index.ntotal}")
print("Database saved successfully!")