from flask import Blueprint, render_template
from controllers.products import ProductController
from flask_login import login_required

main = Blueprint("main", __name__)

shopname = "_Tshop"


@main.route("/")
def index():
    top_products = ProductController.get_popular_products(limit=6)
    return render_template("index.html", shopname=shopname, products=top_products)


@main.route("/home")
@login_required
def home():
    products = ProductController.get_all_products() or []  # Evite None
    total_products = len(products)

    recent_products = ProductController.get_recent_products(limit=6) or []
    return render_template(
        "home.html",
        shopname=shopname,
        total_products=total_products,
        recent_products=recent_products,
    )
