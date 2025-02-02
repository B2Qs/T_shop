from flask import Flask
from models.products import Product
from models import init_db, db
from flask_login import LoginManager
import secrets
from blueprints.main import main
from blueprints.auth import auth
from blueprints.users import users
from blueprints.products import products

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    
    init_db(app)

    # Enregistrement des blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(products)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from models.users import User
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        load_initial_data()
    
    return app

def load_initial_data():
    from models.users import User
    from controllers.products import ProductController
    from sqlalchemy import exc

    # Création de l'utilisateur admin
    try:
        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User(username='admin', email='admin@stackshop.com', role='admin')
            user.set_password('admin')  # Utilisez la méthode set_password
            db.session.add(user)
            db.session.commit()
            print('Utilisateur admin créé avec succès')
    except exc.IntegrityError:
        db.session.rollback()
        print('L\'utilisateur admin existe déjà')
    except Exception as e:
        print(f'Erreur lors de la création de l\'utilisateur admin : {str(e)}')
    
    # Chargement des produits
    try:
        products = ProductController.get_all_products()
        if not products:
            api_products = ProductController.get_all_products()
            for product_data in api_products:
                new_product = Product(
                    title=product_data['title'],
                    price=product_data['price'],
                    description=product_data['description'],
                    category=product_data['category'],
                    image=product_data['image'],
                    rating=product_data['rating']
                )
                db.session.add(new_product)      
            db.session.commit()
            print('Produits chargés avec succès depuis l\'API')
        else:
            print('Produits déjà existants dans la base de données')
    except Exception as e:
        print(f'Erreur lors du chargement des produits : {str(e)}')

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)