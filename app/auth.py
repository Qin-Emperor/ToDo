from flask import Blueprint, render_template, url_for, flash, redirect
from flask_login import login_required, login_user, logout_user
from sqlalchemy import select

from . import login_manager, db
from .forms import RegistrationForm, LoginForm
from .models import User

auth = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.email == form.email.data))
        if user is None:
            new_user = User(
                name=form.username.data,
                email=form.email.data,
                timezone=form.timezone.data
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Акаунт було успішно створено", "success")
            return redirect(url_for('auth.register'))
        else:
            flash("Акаунт з такою поштою вже існує", "error")
            return redirect(url_for('auth.register'))
    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash("Невірний логін або пароль", "error")
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for("main.index"))
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
