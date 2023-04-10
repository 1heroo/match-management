import asyncio
import datetime
import time

import pandas as pd

from comparison_management.utils import CMUtils
from match_management.queries import MatchedProductQueries, ChildMatchedProductQueries
from match_management.utils import MatchUtils
from match_management.xlsx_utils import XlsxUtils


class CMServices:

    def __init__(self):
        self.match_utils = MatchUtils()
        self.cm_utils = CMUtils()
        self.xlsx_utils = XlsxUtils()

        self.matched_product_queries = MatchedProductQueries()
        self.child_matched_product_queries = ChildMatchedProductQueries()

    async def chars_management(self, article_wb):
        the_product = await self.matched_product_queries.get_product_by_nm(nm=article_wb)
        child_matched_products = await self.child_matched_product_queries.get_children_by_parent_nm_id(
            parent_nm_id=article_wb)

        products_json = await self.cm_utils.get_detail_by_nms(
            nms=[product.nm_id for product in [the_product] + child_matched_products])
        products = await self.cm_utils.prepare_chars_for_output(products=products_json)
        return products

    async def not_profitable_management(self, brand_id: int = None) -> list[str]:

        if brand_id is None:
            the_products = await self.matched_product_queries.fetch_all()
        else:
            the_products = await self.matched_product_queries.get_matched_products_by_brand_id(brand_id=brand_id)

        cached_files = []
        for the_product in the_products:
            if the_product.price is None:
                continue

            child_matched_products = await self.child_matched_product_queries.get_children_by_parent_id(
                parent_id=the_product.id)

            suitable_children = await self.cm_utils.not_profitable_check_prices_and_prepare_for_output(
                the_product=the_product, children=child_matched_products)
            if suitable_children:
                file_name = 'cached_files/' + f'{the_product.brand} ' + str(the_product.nm_id)\
                            + '_' +\
                            str(datetime.date.today()) + '.xlsx'

                df = pd.DataFrame(suitable_children)
                df.to_excel(file_name, index=False)
                cached_files.append(file_name)
        return cached_files

    async def profitable_management(self, brand_id: int) -> list[str]:
        matched_products = await self.matched_product_queries.get_matched_products_by_brand_id(brand_id=brand_id)
        cached_files = []
        for the_product in matched_products:
            child_matched_products = await self.child_matched_product_queries.get_children_by_parent_nm_id(
                parent_nm_id=the_product.nm_id)

            suitable_children = await self.cm_utils.profitable_check_prices_and_prepare_for_output(
                the_product=the_product, children=child_matched_products)
            if suitable_children:
                file_name = 'cached_files/' + f'{the_product.brand} ' + str(the_product.nm_id)\
                            + '_' + \
                            str(datetime.date.today()) + '.xlsx'

                df = pd.DataFrame(suitable_children)
                df.to_excel(file_name, index=False)
                cached_files.append(file_name)
        return cached_files

    async def get_recommended_min_prices(self):
        the_products = await self.matched_product_queries.fetch_all()

        output_data = []
        for the_product in the_products:
            if the_product.price is None:
                continue

            child_matched_products = await self.child_matched_product_queries.get_children_by_parent_id(
                parent_id=the_product.id)

            recommended_price_row = await self.cm_utils.not_profitable_matched_products_prepare_recommended_prices(
                the_product=the_product, children=child_matched_products)
            if recommended_price_row:
                output_data.append(recommended_price_row)
        return output_data

    async def get_child_less_than_three(self) -> list[str]:
        matched_products = await self.matched_product_queries.fetch_all()

        cached_files = []
        for the_product in matched_products:
            child_matched_products = await self.child_matched_product_queries.get_children_by_parent_id(
                parent_id=the_product.id)

            if len(child_matched_products) <= 3:

                if not child_matched_products:
                    child_matched_products.append(the_product)

                file_name = 'cached_files/' + f'{the_product.brand} {the_product.nm_id}' \
                            + '_' + \
                            str(datetime.date.today()) + '.xlsx'
                df = pd.DataFrame(
                    self.cm_utils.prepare_output_children(child_products=child_matched_products)
                )
                df.to_excel(file_name, index=False)
                cached_files.append(file_name)
        return cached_files

    async def get_children_by_articles_wb(self, df: pd.DataFrame) -> list[str]:

        cached_files = []
        seria = df['Артикул WB']
        for nm_id in seria:
            the_product = await self.matched_product_queries.get_product_by_nm(nm=nm_id)

            if not the_product:
                continue

            children = await self.child_matched_product_queries.get_children_by_parent_nm_id(parent_nm_id=nm_id)
            df = pd.DataFrame(
                self.cm_utils.prepare_output_children(child_products=children)
            )
            file_name = 'cached_files/' + str(the_product.nm_id) \
                        + '_' + \
                        str(datetime.date.today()) + '.xlsx'

            df.to_excel(file_name, index=False)
            cached_files.append(file_name)
        return cached_files

    async def get_non_existent_articles(self, df: pd.DataFrame) -> list[dict]:
        output_data = []

        for index in df.index:
            nm_id = df['Артикул WB'][index]
            brand = df['Бренд'][index]
            category = df['Предмет'][index]
            vendor_code = df['Артикул продавца'][index]

            matched_product = await self.matched_product_queries.get_product_by_nm(nm=nm_id)
            if matched_product is None:
                output_data.append({
                    'Артикул WB': nm_id,
                    'Артикул продавца': vendor_code,
                    'Бренд': brand,
                    'Предмет': category
                })

        return output_data

