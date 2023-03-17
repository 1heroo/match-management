from sqlalchemy import select, func

from sqladmin import ModelView

from match_management.models import Product, MatchedProduct, ChildMatchedProduct, Brand


class ProductAdmin(ModelView, model=Product):
    page_size = 100
    column_list = ['nm_id', 'product']
    column_searchable_list = ['nm_id']


class MatchedProductAdmin(ModelView, model=MatchedProduct):
    page_size = 100
    column_list = ['nm_id', 'title', 'brand', 'brand_id', 'subj_name', 'subj_root_name', 'min_price', 'price', 'rrc', 'vendor_code', 'checked_nms']
    column_searchable_list = ['nm_id']


class ChildMatchedProductAdmin(ModelView, model=ChildMatchedProduct):
    page_size = 100
    column_list = ['nm_id', 'parent_nm_id', 'brand', 'brand_id', 'title', 'price', 'vendor_name', 'vendor_code']
    column_searchable_list = ['parent_nm_id', 'nm_id']
    column_default_sort = [(ChildMatchedProduct.price, False)]


class BrandAdmin(ModelView, model=Brand):
    page_size = 100
    column_list = ['id', 'title', 'brand_id', 'percentage', 'min_step', 'is_included_to_pm']
