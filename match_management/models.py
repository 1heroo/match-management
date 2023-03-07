from sqlalchemy.orm import relationship

from db.db import Base
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


class Product(Base):
    __tablename__ = 'products'

    id = sa.Column(sa.Integer, primary_key=True)
    nm_id = sa.Column(sa.Integer)
    product = sa.Column(JSONB)


class MatchedProduct(Base):
    __tablename__ = 'matched_products'
    id = sa.Column(sa.Integer, primary_key=True)
    nm_id = sa.Column(sa.Integer)
    title = sa.Column(sa.String)
    subj_name = sa.Column(sa.String)
    subj_root_name = sa.Column(sa.String)
    vendor_code = sa.Column(sa.String)
    min_price = sa.Column(sa.Integer)
    the_product = sa.Column(JSONB)
    matched_products = relationship('ChildMatchedProduct', back_populates='parent')


class ChildMatchedProduct(Base):
    __tablename__ = 'child_matched_products'

    id = sa.Column(sa.Integer, primary_key=True)
    nm_id = sa.Column(sa.Integer)
    title = sa.Column(sa.String)
    vendor_name = sa.Column(sa.String)
    vendor_code = sa.Column(sa.String)
    is_correct = sa.Column(sa.Boolean)
    product = sa.Column(JSONB)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('matched_products.id'))
    parent = relationship('MatchedProduct', back_populates='matched_products')


class Brand(Base):
    __tablename__ = 'brands'

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    percentage = sa.Column(sa.Integer)
    min_step = sa.Column(sa.Integer)
    is_included_to_pm = sa.Column(sa.Boolean)
