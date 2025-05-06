from sqlalchemy import Integer, String, ForeignKey, Boolean, DateTime, Numeric, CheckConstraint
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import List
from datetime import datetime

class Base(DeclarativeBase): 
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)  # Telegram user ID
    name: Mapped[str] = mapped_column(String)



class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    products: Mapped[list['Product']] = relationship(back_populates='category', order_by='Product.name')
    

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[Numeric] = mapped_column(Numeric(10,2), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=True)

    category: Mapped['Category'] = relationship(back_populates='products')

    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
    )


class Favorite(Base):
    __tablename__ = 'favorites'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'), nullable=False)

    product: Mapped[Product] = relationship(Product, lazy='joined')
    

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    total_price: Mapped[Numeric] = mapped_column(Numeric(10,2), nullable=False)

    items = relationship('OrderItem', back_populates='order', lazy='selectin', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint('total_price > 0', name='check_total_price_positive'),
    )


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    price_at_order: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    order = relationship('Order', back_populates='items')
    product = relationship('Product', lazy='selectin')

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('price_at_order >= 0', name='check_price_at_order_positive'),
    )