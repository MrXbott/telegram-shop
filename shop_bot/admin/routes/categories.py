from flask import current_app, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError, DataError
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, raiseload
from db.models import Category
from db.init import sync_session
import logging

from . import routes_bp

logger = logging.getLogger(__name__)

@routes_bp.route('/categories/')
def category_list():
    with sync_session() as session:
        stmt = select(Category).order_by(Category.name)
        categories = session.scalars(stmt).all()
    return render_template('categories.html', categories=categories)



@routes_bp.route('/categories/add/', methods=['GET', 'POST'])
def add_category():
    with sync_session() as session:
        if request.method == 'POST':
            form = request.form
            try:
                name = form['name'].strip()
                if not name:
                    raise ValueError('Название не может быть пустым')
                
                category = Category(name=name)
                session.add(category)
                session.commit()
                logger.info(f'✅ Добавлена новая категория: {category.name} (ID: {category.id})')

            # except DataError as e:
            #     session.rollback()
            #     logger.error(f'❌ Ошибка: цена выше максимально допустимого значения: {e}', exc_info=True)
            #     return f'Ошибка: цена выше максимально допустимого значения: {e}', 400
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f'❌ Ошибка при добавлении категории: {e}', exc_info=True)
                return f'Ошибка при добавлении категории', 400
            except Exception as e:
                return f'{e}', 400
            
            return redirect(url_for('admin.category_list'))
        
        # categories = session.query(Category).all()
        return render_template('add_category.html')
