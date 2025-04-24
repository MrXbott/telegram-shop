from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
from db.models import Product
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
    if request.method == 'POST':
        form = request.form
        try:
            with sync_session() as session:
                product = Product(name=form['name'], price=int(form['price']))
                session.add(product)
                session.commit()
        except SQLAlchemyError as e:
            print(f'Error adding product: {e}')
            # Можно добавить обработку ошибок и откат транзакции
        return redirect(url_for('product_list'))

    return render_template('add_product.html')


if __name__ == '__main__':
    app.run(debug=True)
