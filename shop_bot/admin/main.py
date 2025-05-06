from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, raiseload
from db.models import Product, Category
from db.init import sync_session
from config import MEDIA_FOLDER_PATH
import logging


logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/media/<path:filename>')
def media_products(filename):
    return send_from_directory(MEDIA_FOLDER_PATH, filename)


@app.route('/')
def index():
    return redirect(url_for('product_list'))


@app.route('/products/')
def product_list():
    with sync_session() as session:
        stmt = select(Category).order_by(Category.name).options(selectinload(Category.products))
        categories = session.scalars(stmt).all()
    return render_template('products.html', categories= categories)


@app.route('/products/add/', methods=['GET', 'POST'])
def add_product():
    with sync_session() as session:
        if request.method == 'POST':
            form = request.form
            file = request.files.get('image')
            if file and file.filename != '':
                file_name = secure_filename(file.filename)
                file_path = os.path.join('products/', file_name)
                file.save(os.path.join(MEDIA_FOLDER_PATH, 'products', file_name))

            try:
                name = form['name'].strip()
                price = int(form['price'])
                category_id = int(form['category'])

                if not name:
                    raise ValueError('Название не может быть пустым')

                if price < 0:
                    raise ValueError('Цена не может быть отрицательной')
                
                category = session.query(Category).filter_by(id=category_id).first()
                if not category:
                    logger.warning(f'❗ Категория с ID {category_id} не найдена.')
                    return f'Категория с ID {category_id} не найдена.', 400
                
                product = Product(name=name, 
                                  price=price, 
                                  category_id=category_id, 
                                  image=file_path
                                  )
                session.add(product)
                session.commit()
                logger.info(f'✅ Добавлен новый продукт: {product.name} (ID: {product.id})')

            except (SQLAlchemyError, ValueError) as e:
                session.rollback()
                logger.error(f'❌ Ошибка при добавлении продукта: {e}', exc_info=True)
                return f'Ошибка: {e}', 400
                
            return redirect(url_for('product_list'))
        
        categories = session.query(Category).all()
        return render_template('add_product.html', categories=categories)


if __name__ == '__main__':
    app.run(debug=True)
