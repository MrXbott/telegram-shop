from flask import current_app, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError, DataError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import os
import logging

from db.models import Product, Category
from db.init import sync_session
from exceptions.db.products import NegativeProductPriceError, NegativeProductQuantityError
from . import routes_bp

logger = logging.getLogger(__name__)

@routes_bp.route('/products/')
def product_list():
    logger.info('🔎 Запрошен список продуктов.')
    with sync_session() as session:
        stmt = select(Category).order_by(Category.name).options(selectinload(Category.products))
        categories = session.scalars(stmt).all()
    logger.debug(f'📦 Получено {len(categories)} категорий.')
    return render_template('products.html', categories=categories)

@routes_bp.route('/products/add/', methods=['GET', 'POST'])
def add_product():
    logger.info('➡️ Обработка запроса добавления продукта.')
    with sync_session() as session:
        if request.method == 'POST':
            logger.debug('📥 Обработка POST-запроса для добавления продукта.')
            form = request.form
            file = request.files.get('image')
            file_path = ''
            if file and file.filename != '':
                file_name = secure_filename(file.filename)
                file_path = os.path.join('products/', file_name)
                MEDIA_FOLDER_PATH = current_app.config.get('MEDIA_FOLDER_PATH')
                full_path = os.path.join(MEDIA_FOLDER_PATH, 'products', file_name)
                file.save(full_path)
                logger.info(f'🖼️ Загружено изображение: {file_name}, сохранено в {full_path}')
            try:
                name = form['name'].strip()
                price = int(form['price'])
                category_id = int(form['category'])
                quantity_in_stock = int(form['quantity_in_stock'])

                if not name:
                    logger.warning('⚠️ Попытка добавить продукт без имени.')
                    raise ValueError('Название не может быть пустым')

                if price < 0:
                    logger.warning(f'⚠️ Указана отрицательная цена: {price}')
                    raise NegativeProductPriceError(price)
                
                if quantity_in_stock < 0:
                    logger.warning(f'⚠️ Указано отрицательное количество: {quantity_in_stock}')
                    raise NegativeProductQuantityError(quantity_in_stock)
                
                category = session.query(Category).filter_by(id=category_id).first()
                if not category:
                    logger.warning(f'❌ Категория с ID {category_id} не найдена.')
                    return f'Категория с ID {category_id} не найдена.', 400
                
                product = Product(name=name, 
                                  price=price, 
                                  category_id=category_id, 
                                  quantity_in_stock=quantity_in_stock,
                                  image=file_path
                                  )
                session.add(product)
                session.commit()
                logger.info(f'✅ Добавлен новый продукт: {product.name} (ID: {product.id})')

            except DataError as e:
                session.rollback()
                logger.error(f'❌ Ошибка: цена выше максимально допустимого значения: {e}', exc_info=True)
                return f'Ошибка: цена выше максимально допустимого значения: {e}', 400
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f'❌ Ошибка при добавлении товара: {e}', exc_info=True)
                return f'Ошибка при добавлении товара', 400
            except Exception as e:
                return f'{e}', 400
            
            return redirect(url_for('admin.product_list'))
        
        logger.debug('📄 Обработка GET-запроса — отображение формы добавления продукта.')
        categories = session.query(Category).all()
        return render_template('add_product.html', categories=categories)