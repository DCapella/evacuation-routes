from flask import Flask

from flask_sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_file

db = SQLAlchemy(app)

from app import routes