import click
from flask.cli import with_appcontext
from app import db
from app.models.property import Property
from app.models.property_image import PropertyImage
from app.models.amenity import Amenity

@click.command('reset-db')
@with_appcontext
def reset_db():
    """Пересоздает базу данных."""
    db.drop_all()
    db.create_all()
    click.echo('База данных пересоздана.')

def init_app(app):
    app.cli.add_command(reset_db)