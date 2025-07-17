import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///C:/temp_db_areena/site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    TESTING = False