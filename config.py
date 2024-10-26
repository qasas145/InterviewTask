import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/mydatabase")
