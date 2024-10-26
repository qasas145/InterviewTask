import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "muhammad_elsayed")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "muhammad_elqasas")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/mydatabase")
