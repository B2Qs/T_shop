from flask import Blueprint, jsonify, request, current_app, render_template, redirect, url_for
from flask_login import login_required, current_user
from controllers.products import ProductController
from werkzeug.utils import secure_filename
import os
from utils.decorators import admin_required 

products = Blueprint('products', __name__)

shopname = "_Tshop"

# Definir allowed_file al inicio del archivo
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Actualizar un producto (solo admin)
@products.route('/product/update/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
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

 # Si es GET, mostrar formulario de edición
    return render_template('products/edit_product.html', product=product, shopname=shopname)


# Añadir un nuevo producto (solo admin)
@products.route('/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        product_data = request.form.to_dict()
        # Manejar subida de Imagen
        if 'image' in request.files:
            file = request.files.get('image')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                product_data['image'] = filename
        product = ProductController.add_product(product_data)
        if product:
            return redirect(url_for('main.home'))
        else:
            return render_template('add_product.html', error='Error adding product', shopname=shopname)
    return render_template('products/add_product.html', shopname=shopname)

# Eliminar un producto (solo admin)
@products.route('/product/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    if ProductController.delete_product(product_id):
        return redirect(url_for('main.home'))
    return jsonify({'message': 'Error deleting product'}), 404

# Vista de lista de productos para admin
@products.route('/admin/products', methods=['GET'])
@login_required
@admin_required
def admin_products():
    products = ProductController.get_all_products()
    return render_template('products/admin_products.html', 
                         products=products,
                         shopname=shopname)

# Vista de productos para clientes
@products.route('/shop', methods=['GET'])
def shop():
    products = ProductController.get_all_products()
    return render_template('products/shop.html', 
                         products=products,
                         shopname=shopname)
