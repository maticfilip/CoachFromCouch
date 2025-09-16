from flask_sqlalchemy import SQLAlchemy
from datetime import date


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

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"
    

class Workout(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(120),nullable=False)
    description=db.Column(db.Text)
    start=db.Column(db.DateTime, nullable=False)
    end=db.Column(db.DateTime,nullable=False)
    date=db.Column(db.Date, nullable=False,default=date.today)

    trainer_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trainer=db.relationship("User",foreign_keys=[trainer_id])

    client_id=db.Column(db.Integer, db.ForeignKey("user.id"),nullable=True)
    client=db.relationship("User",foreign_keys=[client_id])

    def __repr__(self):
        return f"<Workout {self.title} from {self.start} to {self.end}>"