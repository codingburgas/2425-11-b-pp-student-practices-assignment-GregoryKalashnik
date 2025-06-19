from extensions import db
from flask_login import UserMixin
from datetime import datetime
 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='student')
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
 
    def is_admin(self):
        return self.role == 'admin'
 
 
class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_on = db.Column(db.DateTime, default=datetime.utcnow)
 
    user = db.relationship('User', backref=db.backref('datasets', lazy=True))
 
 
class ModelData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    mse = db.Column(db.Float, nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
 
    user = db.relationship('User', backref=db.backref('models', lazy=True))
    dataset = db.relationship('Dataset', backref=db.backref('models', lazy=True))