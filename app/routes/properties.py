from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.property import Property, PropertyImage
from app.models.amenity import Amenity
from app import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint('properties', __name__, url_prefix='/properties')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file, folder='properties'):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], folder, unique_filename))
        return unique_filename
    return None

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            property = Property(
                title=request.form['title'],
                description=request.form['description'],
                price=float(request.form['price']),
                city=request.form['city'],
                district=request.form['district'],
                property_type=request.form['property_type'],
                area=float(request.form['area']),
                rooms=int(request.form['rooms']),
                is_short_term=bool(request.form.get('is_short_term')),
                owner_id=current_user.id
            )
            
            # Обработка удобств
            amenity_ids = request.form.getlist('amenities')
            if amenity_ids:
                amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all()
                property.amenities = amenities
            
            db.session.add(property)
            db.session.commit()
            
            # Обработка изображений
            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    filename = save_image(file)
                    if filename:
                        property_image = PropertyImage(filename=filename, property_id=property.id)
                        db.session.add(property_image)
            
            db.session.commit()
            flash('Объявление успешно создано!', 'success')
            return redirect(url_for('properties.view', id=property.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании объявления: {str(e)}', 'danger')
            return redirect(url_for('properties.create'))
    
    amenities = Amenity.query.all()
    return render_template('properties/create.html', amenities=amenities)

@bp.route('/<int:id>')
def view(id):
    property = Property.query.get_or_404(id)
    return render_template('properties/view.html', property=property)

@bp.route('/search')
def search():
    city = request.args.get('city', '')
    property_type = request.args.get('property_type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    is_short_term = request.args.get('is_short_term', type=bool)
    
    query = Property.query
    
    if city:
        query = query.filter(Property.city.ilike(f'%{city}%'))
    if property_type:
        query = query.filter_by(property_type=property_type)
    if min_price is not None:
        query = query.filter(Property.price >= min_price)
    if max_price is not None:
        query = query.filter(Property.price <= max_price)
    if is_short_term is not None:
        query = query.filter_by(is_short_term=is_short_term)
    
    properties = query.order_by(Property.created_at.desc()).all()
    return render_template('properties/search.html', properties=properties)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    property = Property.query.get_or_404(id)
    if property.owner_id != current_user.id:
        flash('У вас нет прав для редактирования этого объявления', 'danger')
        return redirect(url_for('properties.view', id=id))
    
    if request.method == 'POST':
        try:
            property.title = request.form['title']
            property.description = request.form['description']
            property.price = float(request.form['price'])
            property.city = request.form['city']
            property.district = request.form['district']
            property.property_type = request.form['property_type']
            property.area = float(request.form['area'])
            property.rooms = int(request.form['rooms'])
            property.is_short_term = bool(request.form.get('is_short_term'))
            
            # Обновление удобств
            amenity_ids = request.form.getlist('amenities')
            property.amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all() if amenity_ids else []
            
            # Обработка новых изображений
            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    if file and file.filename:
                        filename = save_image(file)
                        if filename:
                            property_image = PropertyImage(filename=filename, property_id=property.id)
                            db.session.add(property_image)
            
            db.session.commit()
            flash('Объявление успешно обновлено!', 'success')
            return redirect(url_for('properties.view', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении объявления: {str(e)}', 'danger')
    
    amenities = Amenity.query.all()
    return render_template('properties/edit.html', property=property, amenities=amenities)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    property = Property.query.get_or_404(id)
    if property.owner_id != current_user.id:
        flash('У вас нет прав для удаления этого объявления', 'danger')
        return redirect(url_for('properties.view', id=id))
    
    try:
        # Удаление изображений с диска
        for image in property.images:
            try:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', image.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting file {image.filename}: {str(e)}")
        
        # Удаление связей с удобствами
        property.amenities = []
        
        # Удаление объявления (каскадно удалит все изображения)
        db.session.delete(property)
        db.session.commit()
        
        flash('Объявление успешно удалено!', 'success')
        return redirect(url_for('profile.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении объявления: {str(e)}', 'danger')
        return redirect(url_for('properties.view', id=id))

@bp.route('/<int:id>/delete_image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(id, image_id):
    property = Property.query.get_or_404(id)
    if property.owner_id != current_user.id:
        flash('У вас нет прав для удаления изображений', 'danger')
        return redirect(url_for('properties.view', id=id))
    
    image = PropertyImage.query.get_or_404(image_id)
    if image.property_id != property.id:
        flash('Изображение не принадлежит данному объявлению', 'danger')
        return redirect(url_for('properties.view', id=id))
    
    try:
        # Удаление файла с диска
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', image.filename))
        except:
            pass
        
        db.session.delete(image)
        db.session.commit()
        flash('Изображение успешно удалено!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении изображения: {str(e)}', 'danger')
    
    return redirect(url_for('properties.edit', id=id))