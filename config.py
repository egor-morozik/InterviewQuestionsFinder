import os
from typing import List

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "mixtral-8x7b-32768"  
    
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = "interview_questions"
    
    TECHNOLOGIES = [
        "Python", "Django", "FastAPI", 
        "SQL", "PostgreSQL", "Redis", 
        "Docker", "Linux", "Git"
    ]
    
    SEARCH_QUERIES = {
        "Python": [
            "python собеседование вопросы ответы",
            "python технические вопросы интервью",
            "python разработчик вопросы на собеседовании"
        ],
        "Django": [
            "django вопросы на собеседовании",
            "django разработчик технические вопросы",
            "django interview questions русский"
        ]
    }
    
    VECTOR_SIZE = 384
    DISTANCE = "Cosine"
    