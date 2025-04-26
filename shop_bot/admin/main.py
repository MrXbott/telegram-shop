from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
from db.models import Product, Category
from db.init import sync_session


app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('product_list'))


@app.route('/products')
def product_list():
    with sync_session() as session:
        products = session.query(Product).all()
    return render_template('products.html', products=products)


@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    with sync_session() as session:
        if request.method == 'POST':
            form = request.form
            try:
                product = Product(name=form['name'], price=int(form['price']), category_id=int(form['category']))
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
