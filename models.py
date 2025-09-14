from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    birthYear = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Client {self.name}>"

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True, nullable=False)
    email=db.Column(db.String(120),unique=True, nullable=False)
    password=db.Column(db.String(200), nullable=False)
    role=db.Column(db.String(20),nullable=False)