from comparison_management.utils import CMUtils
from match_management.queries import MatchedProductQueries, ChildMatchedProductQueries
from match_management.utils import MatchUtils


class CMServices:

    def __init__(self):
        self.match_utils = MatchUtils()
        self.cm_utils = CMUtils()

        self.matched_product_queries = MatchedProductQueries()
        self.child_matched_product_queries = ChildMatchedProductQueries()

    async def chars_management(self, article_wb):
        the_product = await self.matched_product_queries.get_product_by_nm(nm=article_wb)
        child_matched_products = await self.child_matched_product_queries.get_children_by_parent_nm_id(
            parent_nm_id=article_wb)

        products = await self.cm_utils.prepare_chars_for_output(products=[the_product] + child_matched_products)
        return products
