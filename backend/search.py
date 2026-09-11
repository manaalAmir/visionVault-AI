import os
import shutil
import faiss
import pickle
import numpy as np
from embedding import get_text_embedding,get_image_embedding
from ranking import filter_results

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
INDEX_FILE=os.path.join(BASE_DIR,"..","vectors","image_index.faiss")
NAMES_FILE=os.path.join(BASE_DIR,"..","vectors","image_names.pkl")
IMAGE_FOLDER=os.path.join(BASE_DIR,"..","images")
VALID_EXTENSIONS=(".jpg",".jpeg",".png",".webp",".jfif")
index=faiss.read_index(INDEX_FILE)

with open(NAMES_FILE,"rb") as f:
    image_names=pickle.load(f)

print(f"Images loaded:{len(image_names)}")
print(f"Vectors loaded:{index.ntotal}")
def _save_to_disk():
    faiss.write_index(index,INDEX_FILE)
    with open(NAMES_FILE,"wb") as f:
        pickle.dump(image_names,f)

def search_images(query):
    query_vector=get_text_embedding(query).astype("float32")
    faiss.normalize_L2(query_vector)
    k=index.ntotal
    distances,indices=index.search(query_vector,k)
    return filter_results(distances,indices,image_names)

def upload_images(files):
    uploaded=[]
    skipped=[]
    for file in files:
        filename=file.filename
        if filename in image_names:
            skipped.append(filename)
            continue

        save_path=os.path.join(IMAGE_FOLDER,filename)
        with open(save_path,"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        try:
            embedding=get_image_embedding(save_path).astype("float32")
        except Exception as e:
            print(f"Skipping {filename},error:{e}")
            os.remove(save_path)
            continue

        faiss.normalize_L2(embedding)
        index.add(embedding)
        image_names.append(filename)
        uploaded.append(filename)

    _save_to_disk()

    return{
        "uploaded":uploaded,
        "skipped":skipped,
        "total_images":len(image_names)
    }


def add_folder(folder_path):
    if not os.path.isdir(folder_path):
        return {"error":f"Folder not found:{folder_path}"}

    added=[]
    skipped=[]
    failed=[]
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(VALID_EXTENSIONS):
            continue

        if filename in image_names:
            skipped.append(filename)
            continue

        src_path=os.path.join(folder_path,filename)
        dest_path=os.path.join(IMAGE_FOLDER,filename)

        if os.path.abspath(src_path)!=os.path.abspath(dest_path):
            shutil.copyfile(src_path,dest_path)
        try:
            embedding=get_image_embedding(dest_path).astype("float32")
        except Exception as e:
            print(f"Skipping {filename},error:{e}")
            failed.append(filename)
            continue

        faiss.normalize_L2(embedding)
        index.add(embedding)
        image_names.append(filename)
        added.append(filename)

    _save_to_disk()

    return {
        "added":added,
        "skipped":skipped,
        "failed":failed,
        "total_images":len(image_names)
    }