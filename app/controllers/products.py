from itertools import product
from datetime import datetime
import requests
from flask import current_app
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from models.products import Product, db
from sqlalchemy.exc import SQLAlchemyError


class ProductController:
    BASE_URL = "https://fakestoreapi.com/products"

    @staticmethod
    def get_all_products():
        try:
            local_products = Product.query.options(joinedload("*")).all()
            response = requests.get(ProductController.BASE_URL)

            if response.status_code == 200:
                api_products = response.json()
                local_ids = [p.id for p in local_products]

                # Prepare new products with new fields
                new_products = [
                    Product(
                        title=api_product["title"],
                        price =api_product["price"],
                        description=api_product["description"],
                        category=api_product["category"],
                        image=api_product["image"],
                        rating=api_product.get("rating", {}),
                        stock=0,
                        created_by=1,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    for api_product in api_products
                    if api_product["id"] not in local_ids
                ]
                if new_products:
                    db.session.bulk_save_objects(new_products)
                    db.session.commit()
                return Product.query.options(joinedload("*")).all()
            return local_products

        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            db.session.rollback()
            return []
        except requests.RequestException as e:
            current_app.logger.error(f"API request error: {str(e)}")
            return []

    @staticmethod
    def get_product(product_id):
        try:
            with current_app.app_context():
                local_product = Product.query.options(joinedload("*")).get(product_id)
                if local_product:
                    return local_product

                response = requests.get(f"{ProductController.BASE_URL}/{product_id}")
                if response.status_code == 200:
                    api_product = response.json()
                    new_product = Product(
                        title=api_product["title"],
                        price=api_product["price"],
                        description=api_product["description"],
                        category=api_product["category"],
                        image=api_product["image"],
                        rating=api_product.get("rating", {}),
                    )
                    db.session.add(new_product)
                    db.session.commit()
                    return new_product
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            db.session.rollback()
        except requests.RequestException as e:
            current_app.logger.error(f"API request error: {str(e)}")
        return None

    @staticmethod
    def update_product(product_id, product_data):
        try:
            with current_app.app_context():
                product_UP = Product.query.get(product_id)
                if product_UP:
                    for key, value in product_data.items():
                        setattr(product_UP, key, value)
                    db.session.commit()
                    return product_UP
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            db.session.rollback()
        return None

    @staticmethod
    def add_product(product_data):
        try:
            with current_app.app_context():
                new_product = Product(**product_data)
                db.session.add(new_product)
                db.session.commit()
                return new_product
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            db.session.rollback()
        return None

    @staticmethod
    def get_recent_products(limit=8):
        try:
            with current_app.app_context():
                return Product.query.order_by(Product.id.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
        return []

    @staticmethod
    def get_popular_products(limit=8):
        try:
            def rating_extractor(product):
                try: 
                    rating_dict = product.rating
                    if isinstance(rating_dict, dict) and 'rate' in rating_dict:
                        return float(rating_dict['rate'])
                    return 0.0
                except (AttributeError, ValueError):
                    return 0.0
            products = Product.query.options(joinedload("*")).all()

            sorted_products = sorted(products, key=rating_extractor, reverse=True)
            return sorted_products[:limit]
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            return []

    @staticmethod
    def fetch_and_save_products(count=5):
        try:
            with current_app.app_context():
                last_product = Product.query.order_by(Product.id.desc()).first()
                start = last_product.id if last_product else 0

                response = requests.get(
                    ProductController.BASE_URL, params={"limit": count, "offset": start}
                )
                if response.status_code == 200:
                    new_products = response.json()
                    for api_product in new_products:
                        new_product = Product(**api_product)
                        db.session.add(new_product)
                    db.session.commit()
                    return True
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            db.session.rollback()
        except requests.RequestException as e:
            current_app.logger.error(f"API request error: {str(e)}")
        return False

    @staticmethod
    def delete_product(product_id):
        try:
            with current_app.app_context():
                product_delete = Product.query.get(product_id)
                if product_delete:
                    db.session.delete(product_delete)
                    db.session.commit()
                    return True
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            db.session.rollback()
        return False
