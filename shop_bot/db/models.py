from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import List


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
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=True)

    category: Mapped['Category'] = relationship(back_populates='products')


class Favorite(Base):
    __tablename__ = 'favorites'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'), nullable=False)

    product: Mapped[Product] = relationship(Product, lazy='joined')
    
