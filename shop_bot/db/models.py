from sqlalchemy import Integer, String, ForeignKey, Boolean, DateTime, Numeric, CheckConstraint
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, validates
from typing import List
from datetime import datetime
from flask_login import UserMixin


class Base(DeclarativeBase): 
    pass


class Admin(Base, UserMixin):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False) 
    name: Mapped[str] = mapped_column(String)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    products: Mapped[list['Product']] = relationship(back_populates='category', order_by='Product.name')
    

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[Numeric] = mapped_column(Numeric(10,2), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=True)
    image_id: Mapped[str] = mapped_column(String, nullable=True)
    quantity_in_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    category: Mapped['Category'] = relationship(back_populates='products')

    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('quantity_in_stock >= 0', name='check_quantity_in_stock_positive'),
    )


class Favorite(Base):
    __tablename__ = 'favorites'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'), nullable=False)

    product: Mapped[Product] = relationship(Product, lazy='joined')
    

class Address(Base):
    __tablename__ = 'addresses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    is_deleted: Mapped[Boolean] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(User, lazy='selectin')

    @validates('address')
    def validate_address(self, key, value):
        if not value or not value.strip():
            raise ValueError('Адрес не может быть пустым')
        return value.strip()
    
    __table_args__ = (
        CheckConstraint('char_length(trim(address)) > 0', name='check_name_not_empty'),
    )


class OrderStatus(Base):
    __tablename__ = 'order_statuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(30), unique=True, nullable=False) 
    status_name: Mapped[str] = mapped_column(String(100), nullable=False) 

    orders: Mapped[list['Order']] = relationship(back_populates='status')


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status_id: Mapped[int] = mapped_column(ForeignKey('order_statuses.id'), nullable=False)
    address_id: Mapped[int] = mapped_column(Integer, ForeignKey('addresses.id'), nullable=False) 
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    total_price: Mapped[Numeric] = mapped_column(Numeric(10,2), nullable=False)

    items = relationship('OrderItem', back_populates='order', lazy='selectin', cascade='all, delete-orphan')
    status: Mapped['OrderStatus'] = relationship(back_populates='orders', lazy='selectin')
    address: Mapped[Address] = relationship(Address, lazy='joined')

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