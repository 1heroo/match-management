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

    async def not_profitable_management(self, brand_id: int) -> list[str]:
        the_products = await self.matched_product_queries.get_matched_products_by_brand_id(brand_id=brand_id)

        cached_files = []
        for the_product in the_products:
            child_matched_products = await self.child_matched_product_queries.get_children_by_parent_nm_id(
                parent_nm_id=the_product.nm_id)

            suitable_children = await self.cm_utils.check_prices_and_prepare_for_output(
                the_product=the_product, children=child_matched_products)
            if suitable_children:
                file_name = 'cached_files/' + str(the_product.nm_id) \
                            + '_' +\
                            str(datetime.date.today()) + '.xlsx'

                df = pd.DataFrame(suitable_children)
                df.to_excel(file_name, index=False)
                cached_files.append(file_name)
        return cached_files
