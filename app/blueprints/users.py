from flask import Blueprint, render_template
from models.users import User


users = Blueprint('users', __name__)


@users.route('/users')
def index():
    return render_template('users.html', users=User.query.all())


@users.route('/users/<int:user_id>')
def user_detail(user_id):
    return render_template('user_detail.html', user=User.query.get(user_id))