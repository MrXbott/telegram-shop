from flask import current_app, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError, DataError
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, raiseload
from db.models import User
from db.init import sync_session
import logging

from . import routes_bp

logger = logging.getLogger(__name__)

@routes_bp.route('/users/')
def user_list():
    with sync_session() as session:
        stmt = select(User).order_by(User.id)
        users = session.scalars(stmt).all()
    return render_template('users.html', users=users)

