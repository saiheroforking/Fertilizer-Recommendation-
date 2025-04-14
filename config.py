import os

DB_USER = 'postgres'
DB_PASSWORD = '1221'
DB_NAME = 'fertilizer.db'
DB_HOST = 'localhost'  # or 127.0.0.1

SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'a8f0c3b2f7e3d8c9b6d5e4a1c2f1e0d3'

