from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_default_amenities():
    from app.models.amenity import Amenity
    
    default_amenities = [
        {'name': 'Wi-Fi', 'icon': 'fas fa-wifi'},
        {'name': 'Парковка', 'icon': 'fas fa-parking'},
        {'name': 'Кондиционер', 'icon': 'fas fa-snowflake'},
        {'name': 'Стиральная машина', 'icon': 'fas fa-tshirt'},
        {'name': 'Кухня', 'icon': 'fas fa-utensils'},
        {'name': 'Телевизор', 'icon': 'fas fa-tv'},
        {'name': 'Балкон', 'icon': 'fas fa-door-open'},
        {'name': 'Лифт', 'icon': 'fas fa-elevator'}
    ]

    for amenity_data in default_amenities:
        if not Amenity.query.filter_by(name=amenity_data['name']).first():
            amenity = Amenity(**amenity_data)
            db.session.add(amenity)
    
    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Создаем директории для загрузки файлов
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'properties'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

    from app.routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    with app.app_context():
        db.create_all()
        create_default_amenities()

    return app