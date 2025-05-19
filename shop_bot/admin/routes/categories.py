from flask import render_template, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from db.models import Category
from db.init import sync_session
import logging

from . import routes_bp

logger = logging.getLogger(__name__)

@routes_bp.route('/categories/')
def category_list():
    logger.info('📂 Запрошен список категорий.')
    with sync_session() as session:
        stmt = select(Category).order_by(Category.name)
        categories = session.scalars(stmt).all()
        logger.debug(f'📦 Получено {len(categories)} категорий из базы.')
    return render_template('categories.html', categories=categories)

@routes_bp.route('/categories/add/', methods=['GET', 'POST'])
def add_category():
    logger.info('➡️ Обработка запроса добавления категории.')
    with sync_session() as session:
        if request.method == 'POST':
            logger.debug('📥 Обработка POST-запроса для добавления категории.')
            form = request.form
            try:
                name = form['name'].strip()
                if not name:
                    logger.warning('⚠️ Попытка добавить категорию без имени.')
                    raise ValueError('Название не может быть пустым')
                
                category = Category(name=name)
                session.add(category)
                session.commit()
                logger.info(f'✅ Добавлена новая категория: {category.name} (ID: {category.id})')

            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f'❌ Ошибка при добавлении категории: {e}', exc_info=True)
                return f'Ошибка при добавлении категории', 400
            except Exception as e:
                return f'{e}', 400
            
            return redirect(url_for('admin.category_list'))
        
        logger.debug('📄 Обработка GET-запроса — отображение формы добавления категории.')
        return render_template('add_category.html')
