from app.routes.auth import bp as auth_bp
from app.routes.properties import bp as properties_bp
from app.routes.chat import bp as chat_bp
from app.routes.profile import bp as profile_bp
from app.routes.main import bp as main_bp

blueprints = [auth_bp, properties_bp, chat_bp, profile_bp, main_bp]