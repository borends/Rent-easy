from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.property import Property
from app import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint('profile', __name__, url_prefix='/profile')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/')
@login_required
def index():
    return render_template('profile/index.html', user=current_user)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        try:
            current_user.first_name = request.form.get('first_name', '').strip()
            current_user.last_name = request.form.get('last_name', '').strip()
            current_user.phone = request.form.get('phone', '').strip()
            
            # Обработка загрузки аватара
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    
                    # Удаляем старый аватар, если он есть
                    if current_user.avatar:
                        try:
                            old_avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', current_user.avatar)
                            if os.path.exists(old_avatar_path):
                                os.remove(old_avatar_path)
                        except Exception as e:
                            print(f"Error removing old avatar: {e}")
                    
                    # Сохраняем новый аватар
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', unique_filename))
                    current_user.avatar = unique_filename

            db.session.commit()
            flash('Профиль успешно обновлен!', 'success')
            return redirect(url_for('profile.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении профиля: {str(e)}', 'danger')
            
    return render_template('profile/edit.html')

@bp.route('/properties')
@login_required
def properties():
    user_properties = Property.query.filter_by(owner_id=current_user.id).all()
    return render_template('profile/properties.html', properties=user_properties)

@bp.route('/<int:user_id>')
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    properties = Property.query.filter_by(owner_id=user_id).order_by(Property.created_at.desc()).all()
    return render_template('profile/view.html', user=user, properties=properties)