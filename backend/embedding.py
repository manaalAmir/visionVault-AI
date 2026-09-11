import torch
import open_clip
from PIL import Image

device="cuda" if torch.cuda.is_available() else "cpu"
model,_,preprocess=open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)
model=model.to(device)
tokenizer=open_clip.get_tokenizer("ViT-B-32")

def get_image_embedding(image_path):
    image=preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding=model.encode_image(image)
    embedding /=embedding.norm(dim=-1,keepdim=True)
    return embedding.cpu().numpy()

def get_text_embedding(text):
    tokens=tokenizer([text]).to(device)
    with torch.no_grad():
        embedding=model.encode_text(tokens)
    embedding /=embedding.norm(dim=-1,keepdim=True)
    return embedding.cpu().numpy()