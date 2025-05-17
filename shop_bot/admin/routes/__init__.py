from flask import Blueprint

routes_bp = Blueprint('admin', __name__)

from . import main, products, users, categories