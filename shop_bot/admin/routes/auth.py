from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import select

from . import routes_bp
from db.models import Admin
from db.init import sync_session
from forms.passwords import ChangePasswordForm

@routes_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_main'))  
    
    if request.method == 'POST':
        with sync_session() as session:
            admin = session.scalar(select(Admin).where(Admin.username==request.form['username']))
            if admin and check_password_hash(admin.password, request.form['password']) and admin.is_active:
                login_user(admin)
                return redirect(url_for('admin.admin_main'))
            flash('Invalid credentials or not an admin')
    return render_template('login.html')

@routes_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@routes_bp.route('/change-password/', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            form.current_password.errors.append('Incorrect current password')
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            with sync_session() as session: 
                session.add(current_user)
                session.commit()
            flash('Password changed successfully. Please log in again.')
            logout_user()
            return redirect(url_for('admin.login'))

    return render_template('change_password.html', form=form)
    
