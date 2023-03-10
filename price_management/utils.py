import math

import aiohttp


class PMUtils:

    @staticmethod
    async def get_min_product(matched_products):
        matched_products = [product for product in matched_products if product['detail'].get('salePriceU')]
        min_product = min(matched_products, key=lambda item: item['detail'].get('salePriceU'))
        return min_product

    @staticmethod
    async def calculate_price(my_price, the_product_min_price, min_price, percentage, min_step):
        percentage = min_price * percentage / 100
        percentage = min_step if percentage > min_step else percentage

        my_price = min_price - percentage

        final_price = the_product_min_price if the_product_min_price >= my_price else my_price
        return int(final_price)

    @staticmethod
    async def calculate_back_price(price, clientSale, basicSale):
        basicSale = 31

        first_price = price / (100 - clientSale) * 100
        price = math.ceil(first_price / (100 - basicSale) * 100)
        return price


class WbAPIUtils:

    @staticmethod
    def api_auth(token):
        return {
            'Authorization': token
        }

    @staticmethod
    async def update_prices(prices, token_auth):
        url = 'https://suppliers-api.wildberries.ru/public/api/v1/prices'

        async with aiohttp.ClientSession(trust_env=True, headers=token_auth) as session:
            len_prices = len(prices)
            times = len_prices // 1000
            start = 0

            for i in range(times + 1):
                chunk_prices = prices[start: start + 1000] if i != times else prices[start: len_prices]
                start += 1000
                async with session.post(url=url, json=chunk_prices) as response:
                    print(await response.text())

    @staticmethod
    async def update_discounts(discounts, token_auth):
        url = 'https://suppliers-api.wildberries.ru/public/api/v1/updateDiscounts'

        async with aiohttp.ClientSession(trust_env=True, headers=token_auth) as session:
            len_discounts = len(discounts)
            times = len_discounts // 1000
            start = 0

            for i in range(times + 1):
                chunk_discounts = discounts[start: start + 1000] if i != times else discounts[start: len_discounts]
                start += 1000

                async with session.post(url=url, json=chunk_discounts) as response:
                    print(await response.text())