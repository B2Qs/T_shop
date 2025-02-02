from flask import current_app
from models.users import User, db
from sqlalchemy.exc import SQLAlchemyError

class UserController:
    @staticmethod
    def get_Users():
        try:
            with current_app.app_context():
                return User.query.all()
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in get_Users: {str(e)}")

    @staticmethod
    def get_Users_by_id(id):
        try:
            with current_app.app_context():
                return User.query(id)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in get_Users_by_id: {str(e)}")
        return None
    
    @staticmethod
    def get_user_by_username(username):
        try:
            with current_app.app_context():
                return User.query.filter_by(username=username).first()
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in get_user_by_username: {str(e)}")
        return None

    @staticmethod
    def add_user(username, password, email, role):
        try:
            with current_app.app_context():
                new_user = User(
                    username=username,
                    password=password,
                    email=email,
                    role=role
                )
                db.session.add(new_user)
                db.session.commit()
                return True
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in add_user: {str(e)}")
            db.session.rollback()
        return False
    
    @staticmethod
    def update_user(id, username, password, email, role):
        try:
            with current_app.app_context():
                user = User.query.get(id)
                if user:
                    user.username = username
                    user.password = password
                    user.email = email
                    user.role = role
                    db.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in update_user: {str(e)}")
            db.session.rollback()
        return False

    @staticmethod
    def delete_user(id):
        try:
            with current_app.app_context():
                user = User.query.get(id)
                if user:
                    db.session.delete(user)
                    db.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in delete_user: {str(e)}")
            db.session.rollback()
        return False
