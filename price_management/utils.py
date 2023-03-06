

class PMUtils:

    @staticmethod
    async def get_the_product_and_min(matched_product):
        the_product = matched_product.the_product
        matched_products = matched_product.matched_products

        min_product = min(matched_products, key=lambda item: item['detail']['salePriceU'])
        return the_product, min_product

    @staticmethod
    async def calculate_price(my_price, min_price):
        percents = min_price * 3 / 100

        my_price = my_price - 100 if percents < 100 else my_price - percents

        return my_price, percents
