from match_management.queries import MatchedProductQueries
from price_management.utils import PMUtils


class PMServices:
    def __init__(self):
        self.pm_utils = PMUtils()
        self.matched_product_queries = MatchedProductQueries()

    async def price_management(self):
        matched_product = await self.matched_product_queries.get_product_by_nm(nm=149031487)
        # matched_product = await self.matched_product_queries.get_all_matched()

        # for matched_product in matched_products:
        the_product, min_product = await self.pm_utils.get_the_product_and_min(matched_product=matched_product)

        my_price = the_product['detail']['salePriceU'] / 100
        min_price = min_product['detail']['salePriceU'] / 100

        print(my_price, min_price)
        calculated_price, percents = await self.pm_utils.calculate_price(my_price=my_price, min_price=min_price)
        return {
            'артикул': 149031487,
            'артикул конкурента': min_product['card']['nm_id'],
            'наша цена до скидки': the_product['detail']['priceU'] / 100,
            'цена конкурента': min_price,
            'итоговая цена после расчета': calculated_price,
            'процентаж': percents
        }
