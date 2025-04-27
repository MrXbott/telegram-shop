from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
# from dotenv import load_dotenv
from db.models import Product, Category
from db.init import sync_session
from config import MEDIA_FOLDER_PATH

# load_dotenv()

app = Flask(__name__)

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
# MEDIA_FOLDER = os.getenv('MEDIA_FOLDER')
# MEDIA_FOLDER_PATH = os.path.join(BASE_DIR, MEDIA_FOLDER)

@app.route('/media/<path:filename>')
def media_products(filename):
    return send_from_directory(MEDIA_FOLDER_PATH, filename)


@app.route('/')
def index():
    return redirect(url_for('product_list'))


@app.route('/products/')
def product_list():
    with sync_session() as session:
        products = session.query(Product).all()
    return render_template('products.html', products=products)


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
                product = Product(name=form['name'], 
                                  price=int(form['price']), 
                                  category_id=int(form['category']), 
                                  image=file_path
                                  )
                session.add(product)
                session.commit()
            except SQLAlchemyError as e:
                # Можно добавить обработку ошибок и откат транзакции
                print(f'Error adding product: {e}')
                
            return redirect(url_for('product_list'))
        
        categories = session.query(Category).all()
        return render_template('add_product.html', categories=categories)


if __name__ == '__main__':
    app.run(debug=True)
