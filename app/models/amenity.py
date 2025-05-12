from app import db

property_amenities = db.Table('property_amenities',
    db.Column('property_id', db.Integer, db.ForeignKey('property.id')),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'))
)

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    icon = db.Column(db.String(64))  # CSS класс для иконки