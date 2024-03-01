
from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dependencies import db


class Categories(db.Model):
    __tablename__ = "categories"

    id = mapped_column(Integer, primary_key=True)
    category_name = mapped_column(String, unique=True)

    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="categories")

    def __init__(self, category_name):
        self.category_name = category_name

    @classmethod
    def create_category(cls, category_name):
        new_category = cls(category_name=category_name)
        db.session.add(new_category)
        db.session.commit()
        return new_category

    @staticmethod
    def get_all_categories():
        categories = Categories.query.all()
        return categories

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}