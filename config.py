import os

# get base dir of this folder
basedir = os.path.abspath(os.path.dirname(__file__))
# c:\Users\Owner\Documents\codingtemple\week6\flask-blog-api

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
