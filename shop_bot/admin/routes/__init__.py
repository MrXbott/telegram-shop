from flask import Blueprint

routes_bp = Blueprint('admin', __name__)

from . import auth, main, products, users, categories