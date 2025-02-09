from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/products")
@login_required
@admin_required
def admin_products():
    return render_template("admin/products.html")
    # pass
