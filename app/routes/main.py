from flask import Blueprint, render_template
from app.models.property import Property

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    properties = Property.query.order_by(Property.created_at.desc()).limit(8).all()
    return render_template('main/index.html', properties=properties)