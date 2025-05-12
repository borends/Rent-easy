from app import db
from datetime import datetime

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(64), nullable=False)
    district = db.Column(db.String(64))
    property_type = db.Column(db.String(20), nullable=False)  # квартира, дом, комната
    area = db.Column(db.Float)  # площадь в м²
    rooms = db.Column(db.Integer)
    is_short_term = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Внешние ключи
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Связи с каскадным удалением
    images = db.relationship('PropertyImage', backref='property', lazy=True, 
                           cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary='property_amenities')

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)