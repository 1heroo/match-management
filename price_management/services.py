from match_management.queries import MatchedProductQueries, BrandQueries, ChildMatchedProductQueries
from match_management.utils import MatchUtils
from price_management.utils import PMUtils, WbAPIUtils
from core.settings import settings


class PMServices:

    def __init__(self):
        self.pm_utils = PMUtils()
        self.match_utils = MatchUtils()
        self.matched_product_queries = MatchedProductQueries()
        self.brand_queries = BrandQueries()
        self.child_matched_products_queries = ChildMatchedProductQueries()

        self.wb_api_utils = WbAPIUtils()

    async def price_management(self):
        wb_standard_auth = self.wb_api_utils.api_auth(token=settings.WB_STANDARD_API_TOKEN)

        matched_products = await self.matched_product_queries.fetch_all()
        # matched_products = matched_products[:1]
        print(matched_products)
        for the_product in matched_products:
            await self.update_price(the_product=the_product, wb_standard_auth=wb_standard_auth)

    async def update_price(self, the_product, wb_standard_auth):
        brand = await self.brand_queries.get_brand_by_brand_id(
            brand_id=the_product.the_product['detail'].get('brandId'), included_to_pm=True)
        print(brand)
        if not brand:
            return
        the_product_json = await self.match_utils.get_product_data(article=the_product.nm_id)

        child_matched_products = await self.child_matched_products_queries.get_children_by_parent_id(
            parent_id=the_product.id)

        if not child_matched_products:
            return

        child_matched_products_json = await self.match_utils.get_detail_by_nms(
            nms=[product.nm_id for product in child_matched_products])

        min_product_json = await self.pm_utils.get_min_product(matched_products=child_matched_products_json)

        my_price = the_product_json['detail'].get('salePriceU')
        min_price = min_product_json['detail'].get('salePriceU')

        if not my_price or not min_price:
            return
        else:
            my_price /= 100
            min_price /= 100

        print('my price', my_price)
        print('min price', min_price)

        if my_price < min_price:
            print('SKIDYYYSH', '\n\n\n')
            return

        if the_product.min_price < min_price:
            calculated_price = await self.pm_utils.calculate_price(
                my_price=my_price, min_price=min_price, the_product_min_price=the_product.min_price,
                percentage=brand.percentage, min_step=brand.min_step
            )
        else:
            calculated_price = the_product.min_price

        extended = the_product_json['detail'].get('extended')

        price_before_discount = await self.pm_utils.calculate_back_price(
            price=calculated_price, clientSale=extended.get('clientSale'), basicSale=extended.get('basicSale'))

        print(price_before_discount)
        await self.wb_api_utils.update_prices(
            prices=[{
                'nmId': the_product.nm_id,
                'price': price_before_discount
            }],
            token_auth=wb_standard_auth
        )

        await self.wb_api_utils.update_discounts(
            discounts=[{
                'nm': the_product.nm_id,
                'discount': 31
            }],
            token_auth=wb_standard_auth
        )
