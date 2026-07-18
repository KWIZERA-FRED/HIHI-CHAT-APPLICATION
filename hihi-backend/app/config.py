import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False