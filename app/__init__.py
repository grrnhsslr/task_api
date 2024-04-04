from flask import Flask  # Import the Flask class from the flask module
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

# Create an instance of Flask called app which will be the central object
app = Flask(__name__)
# set the config for the app
app.config.from_object(Config)

# create an instance of SQLalchemy called db which will be the central obj for our database
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# import the routes to the app
from . import routes, models
