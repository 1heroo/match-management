from sqladmin import ModelView

from match_management.models import Product, MatchedProduct, ChildMatchedProduct, Brand


class ProductAdmin(ModelView, model=Product):

    column_list = ['nm_id', 'product']


class MatchedProductAdmin(ModelView, model=MatchedProduct):
    column_list = ['nm_id', 'title', 'subj_name', 'subj_root_name', 'vendor_code', 'min_price', 'the_product']


class ChildMatchedProductAdmin(ModelView, model=ChildMatchedProduct):
    column_list = ['nm_id', 'title', 'vendor_name', 'vendor_code', 'is_correct', 'product', 'parent_nm_id']


class BrandAdmin(ModelView, model=Brand):
    column_list = ['id', 'title', 'percentage', 'min_step', 'is_included_to_pm']
