from embedding import get_image_embedding
from embedding import get_text_embedding

vector=get_text_embedding("women working in STEM")
print("Vector shape:",vector.shape)
print(vector)