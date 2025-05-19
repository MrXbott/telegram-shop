from flask import render_template
from sqlalchemy import select
import logging

from db.models import User
from db.init import sync_session
from . import routes_bp

logger = logging.getLogger(__name__)

@routes_bp.route('/users/')
def user_list():
    logger.info('🔎 Запрошен список пользователей.')
    with sync_session() as session:
        stmt = select(User).order_by(User.id)
        users = session.scalars(stmt).all()
        logger.debug(f'📦 Получено {len(users)} пользователей из базы.')
    return render_template('users.html', users=users)

