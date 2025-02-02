from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from controllers.products import ProductController

products = Blueprint('products', __name__)

shopname = "_Tshop"

@products.route('/products', methods=['GET'])
def get_products():
    products = ProductController.get_all_products()
    return jsonify([product.to_dict() for product in products])

@products.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = ProductController.get_product(product_id)
    if product:
        return render_template('product.html', shopname=shopname, product=product)
    else:
        return jsonify({'message': 'Product not found'})

@products.route('/product/update/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = ProductController.get_product(product_id)
    if not product:
        return redirect(url_for('main.index', error='Product not found'))
    if request.method == 'POST':
        product_data = request.form.to_dict()
        update_product = ProductController.update_product(product_id, product_data)
        if update_product:
            return redirect(url_for('main.home'))
        else:
            return redirect(url_for('products.add_product', error='Product not found'))

@products.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        product_data = request.get_json()
        product = ProductController.add_product(product_data)
        if product:
            return redirect(url_for('main.home'))
        else:
            return redirect(url_for('products.add_product', error='Product already exists'))
    else:
        return render_template('product.html', shopname=shopname, user=current_user, error=request.args.get('error'))

@products.route('/delete/<int:product_id>', methods=['GET'])
@login_required
def delete_product(product_id):
    deleted = ProductController.delete_product(product_id)
    if deleted:
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.index', error='Product not found'))