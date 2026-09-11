import os              
import time
from PIL import Image

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER=os.path.join(BASE_DIR,"..","images")
MIN_SCORE=0.22  

def find_cutoff(scores):
    if len(scores)<=1:
        return len(scores)

    drops=[]
    for i in range(len(scores)-1):
        drop=scores[i]-scores[i+1]
        drops.append(drop)
    biggest_drop=max(drops)
    cutoff=drops.index(biggest_drop)+1
    return cutoff

def filter_results(scores,indices,image_names,min_score=MIN_SCORE):
    start_time=time.time()
    scores=scores[0]
    indices=indices[0]
    cutoff=find_cutoff(scores)

    result=[]
    for i in range(cutoff):
        if indices[i]==-1:
            continue

        score=float(scores[i])
        if score<min_score:
            continue

        image_path=os.path.join(IMAGE_FOLDER,image_names[indices[i]])
        with Image.open(image_path) as img:
            width,height=img.size

        result.append({
            "image":image_names[indices[i]],
            "score":score,
            "url":f"http://127.0.0.1:8000/images/{image_names[indices[i]]}",
            "width":width,
            "height":height,
            "type":image_names[indices[i]].split(".")[-1].lower()
        })

    search_time=round((time.time()-start_time)*1000,2)

    return{
        "count":len(result),
        "search_time_ms":search_time,
        "results":result
    }