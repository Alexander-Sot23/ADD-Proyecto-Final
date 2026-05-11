from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Registro(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    temperatura = db.Column(db.Float, nullable=False)
    humedad     = db.Column(db.Float, nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.now)

class Config(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(64), unique=True, nullable=False)
    valor = db.Column(db.String(256), nullable=False)
