from urllib.parse import urlparse
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.users import User
from models import db
from forms.login_form import LoginForm
from forms.register_form import RegisterForm

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        print("Formulario validado correctamente")
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash("Login successful", "success")
            next_page = request.args.get("next")
            if not next_page or urlparse(next_page).netloc != "":
                next_page = url_for("main.home")
            return redirect(next_page)
        else:
            flash("Invalid username or password", "danger")
    else:
        if request.method == "POST": 
            print("Errores en el formulario:", form.errors)
    return render_template("accounts/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('The username is already in use', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            email=email,
            password=password,
            role="user",
        )
        new_user.set_password(form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'danger')
            return redirect(url_for('auth.register'))

    return render_template("accounts/register.html", form=form)
