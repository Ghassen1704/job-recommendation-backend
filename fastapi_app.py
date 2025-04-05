from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI()

# Load a BERT-based model for job recommendation
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Dummy job descriptions
job_descriptions = [
    {"id": 1, "title": "Software Engineer", "desc": "Python, Django, REST APIs"},
    {"id": 2, "title": "Data Scientist", "desc": "Machine Learning, TensorFlow, NLP"},
]

# Compute job embeddings
job_embeddings = np.array([model.encode(job["desc"]) for job in job_descriptions])

# Pydantic model to define the expected input
class ResumeRequest(BaseModel):
    resume_text: str

@app.post("/recommend/")
async def recommend_jobs(request: ResumeRequest):
    """Returns top matching jobs for a given resume"""
    resume_embedding = model.encode(request.resume_text)
    scores = np.dot(job_embeddings, resume_embedding)
    
    # Get top 3 jobs
    top_jobs = [job_descriptions[i] for i in np.argsort(scores)[-3:][::-1]]
    
    return {"recommended_jobs": top_jobs}
