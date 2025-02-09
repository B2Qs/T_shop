from flask import Flask

# from models.products import Product
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import init_db, db
from datetime import datetime
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from blueprints.main import main
from blueprints.auth import auth
from blueprints.users import users
from blueprints.products import products

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")  # secrets.token_hex(16)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL"
    )  # "sqlite:///database.db"

    db.init_app(app)
    migrate.init_app(app, db)
    # init_db(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Fonction de chargement d'utilisateur
    @login_manager.user_loader
    def load_user(user_id):
        from models.users import User

        return User.query.get(int(user_id))

    # Enregistrement des blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(products)

    with app.app_context():
        db.create_all()
        load_initial_data()

    return app


def load_initial_data():
    from models.products import Product
    from models.users import User
    from controllers.products import ProductController
    from sqlalchemy import exc

    # Création de l'utilisateur admin
    admin_id = None
    try:
        user = User.query.filter_by(username="admin").first()
        if not user:
            user = User(
                username="admin", password="", email="admin@stackshop.com", role="admin"
            )
            user.set_password("admin")  # Utilisez la méthode set_password
            db.session.add(user)
            db.session.commit()
            admin_id = user.id
            print("Utilisateur admin créé avec succès")
        else:
            admin_id = user.id
    except exc.IntegrityError:
        db.session.rollback()
        print("L'utilisateur admin existe déjà")
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur admin : {str(e)}")

    # Chargement des produits
    try:
        products = ProductController.get_all_products()
        if not products:
            api_products = ProductController.get_all_products()

            for product_data in api_products:
                new_product = Product(
                    title=product_data["title"],
                    price=product_data["price"],
                    description=product_data["description"],
                    category=product_data["category"],
                    image=product_data["image"],
                    rating=product_data["rating"],
                    stock=10,  # Valè pa defo
                    created_by=1,  # ID admin
                    created_at=datetime.utcnow(),
                )
                db.session.add(new_product)
            db.session.commit()
            print("Produits chargés avec succès depuis l'API")
        else:
            print("Produits déjà existants dans la base de données")

        if products:
            print("Produits chargés depuis la base de données")
            print(f"Nombre de produits chargés : {len(products)}")
        else:
            print("Aucun produit chargé")

    except Exception as e:
        print(f"Erreur lors du chargement des produits : {str(e)}")
