from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from auth import auth_bp
from extensions import db
from forms.auth_forms import LoginForm, RegisterForm
from models.models import User
 
auth_bp = Blueprint('auth', __name__, template_folder='templates')
 
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Успешен вход!")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Невалиден имейл или парола.")
            return render_template('auth/login.html', form=form)
 
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Имейлът вече съществува.")
        else:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role=form.role.data
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Успешна регистрация! Влезте сега.")
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
 
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Излязохте успешно.")
    return redirect(url_for('auth.login'))