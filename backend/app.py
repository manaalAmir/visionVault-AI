import os
from typing import List
from fastapi import FastAPI,File,UploadFile
from pydantic import BaseModel
from search import search_images,upload_images,add_folder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/images",
    StaticFiles(directory=os.path.join(BASE_DIR, "..", "images")),
    name="images"
)

class FolderRequest(BaseModel):
    path:str

@app.get("/")
def home():
    return{
        "message":"VisionVault AI is running!"
    }

@app.get("/search")
def search(query:str):
    results=search_images(query)
    return{
        "query":query,
        "results":results
    }

@app.post("/upload")
def upload(files:List[UploadFile]=File(...)):
    return upload_images(files)

@app.post("/add-folder")
def add_folder_route(request:FolderRequest):
    return add_folder(request.path)