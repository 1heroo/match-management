import asyncio

from match_management.queries import ProductQueries, MatchedProductQueries
from match_management.utils import MatchUtils
from match_management.models import MatchedProduct


class FilterLevels:

    @staticmethod
    def first_lvl(the_product, products):
        matched, unmatched = [], []

        for product in products:
            vendorCode1 = product['card'].get('vendor_code')
            vendorCode2 = the_product['card'].get('vendor_code').split('bland')[-1]

            if not vendorCode1:
                continue

            if vendorCode2 in vendorCode1\
                    and product['detail'].get('brand') == the_product['detail'].get('brand') \
                    and product['card'].get('subj_name') == the_product['card'].get('subj_name'):
                    # and product['card']['subj_root_name'] == the_product['card']['subj_root_name']:

                matched.append(product)
            else:
                unmatched.append(product)
        return matched, unmatched

    @staticmethod
    def second_lvl(the_product, products):
        grouped_options = the_product['card'].get('grouped_options', [])
        model1 = None
        matched, unmatched = [], []

        for grouped_option in grouped_options:
            options = grouped_option.get('options', [])
            for option in options:
                if option.get('name') == 'Модель':
                    model1 = option.get('value')

        if not model1:
            return matched, products

        for product in products:
            model2 = None
            grouped_options = product['card'].get('grouped_options', [])
            for grouped_option in grouped_options:
                options = grouped_option.get('options', [])
                for option in options:
                    if option.get('name') == 'Модель':
                        model2 = option.get('value')
            if not model2:
                continue

            product_description = product['card'].get('description')
            if not product_description:
                continue

            if model2 == model1 and the_product['detail'].get('brand') == product['detail'].get('brand') \
                    and model2 in product_description \
                    and model2 in product['card'].get('imt_name'):
                matched.append(product)
            else:
                unmatched.append(product)
        return matched, unmatched

    @staticmethod
    def extra_filter(similar_products, matched):
        pass


class MatchServices:

    def __init__(self):
        self.match_utils = MatchUtils()
        self.filter_lvl = FilterLevels()
        self.product_queries = ProductQueries()
        self.matched_product_queries = MatchedProductQueries()

    async def find_matches(self, df, article_column, min_price_column):
        for index in df.index:
            article = int(df[article_column][index])
            min_price = int(df[min_price_column][index])
            print(article)

            the_product, matched = await self.match_management(article=article)

            the_product, matched_products = await self.match_utils.prepare_matched_products(
                the_product=the_product, matched_products=matched, min_price=min_price)

            await self.matched_product_queries.save_or_update(matched_products=[the_product])
            await self.product_queries.save_in_db(instances=matched_products, many=True)
            await self.product_queries.delete_by_nms([
                product['card']['nm_id'] for product in matched
            ])

    async def match_management(self, article):
        _, matched = await self.find_similar_to_article(article=article)
        # prepared_matches = await self.match_utils.prepare_output(products=matched)

        the_product, matched_by_wb_recs = await self.check_by_identical_nms(matched=matched, main_article=article)
        # prepared_matches_by_wb_recs = await self.match_utils.prepare_output(products=matched_by_wb_recs)

        # uneeded
        # matched_by_visual, _ = await self.check_by_visual_similar(main_article=article)
        # prepared_matches_by_similar = await self.match_utils.prepare_output(products=matched_by_visual)

        # matched_by_search, _ = await self.check_by_search(main_article=article)
        # prepared_matches_by_search = await self.match_utils.prepare_output(products=matched_by_search)

        # matched = prepared_matches + prepared_matches_by_wb_recs  # + prepared_matches_by_similar + prepared_matches_by_search
        # matched = await self.remove_duplicate_nms(products=matched)
        matched = await self.remove_duplicate_nms(products=matched + matched_by_wb_recs)
        return the_product, matched

    async def find_similar_to_article(self, article, products=None):
        the_product = await self.match_utils.get_product_data(article=article)
        if not bool(products):
            # products = await self.match_utils.get_products()
            products = [product.product for product in await self.product_queries.get_all_unmatched_products()]
        output_data = []

        # FIRST LEVEL
        matched, products = self.filter_lvl.first_lvl(the_product=the_product, products=products)
        output_data += matched

        # SECOND LEVEL
        matched, products = self.filter_lvl.second_lvl(the_product=the_product, products=products)
        output_data += matched

        return the_product, output_data

    async def check_by_identical_nms(self, matched, main_article):
        identical_nms = []
        for product in matched:
            identical_nms += await self.match_utils.get_identical(article=product['card']['nm_id'])

        products = []

        tasks = []
        count = 1
        for article in identical_nms:
            task = asyncio.create_task(self.match_utils.get_product_data(article=article))
            tasks.append(task)
            count += 1

            if count % 50 == 0:
                print(count, 'checked_by_identical')
                products += await asyncio.gather(*tasks)
                tasks = []

        products += await asyncio.gather(*tasks)

        matched, unmatched = await self.find_similar_to_article(article=main_article, products=products)
        return matched, unmatched

    async def check_by_visual_similar(self, main_article):
        nm_ids = await self.match_utils.get_in_visual_similar(article=main_article)

        products = []
        tasks = []
        count = 1
        for article in nm_ids:
            task = asyncio.create_task(self.match_utils.get_product_data(article=article))
            tasks.append(task)
            count += 1

            if count % 50 == 0:
                print(count, 'visual')
                products += await asyncio.gather(*tasks)
                tasks = []

        products += await asyncio.gather(*tasks)

        matched, unmatched = await self.find_similar_to_article(article=main_article, products=products)
        return matched, unmatched

    async def check_by_search(self, main_article):
        the_product = await self.match_utils.get_product_data(article=main_article)

        model = None
        grouped_options = the_product['card'].get('grouped_options', [])
        for grouped_option in grouped_options:
            options = grouped_option.get('options', [])
            for option in options:
                if option.get('name') == 'Модель':
                    model = option.get('value')

        if not model:
            return [], []

        nm_ids = await self.match_utils.get_in_search(query=the_product['detail']['brand'] + model)

        products = []
        tasks = []
        count = 1
        for article in nm_ids:
            task = asyncio.create_task(self.match_utils.get_product_data(article=article))
            tasks.append(task)
            count += 1

            if count % 50 == 0:
                print(count, 'search')
                products += await asyncio.gather(*tasks)
                tasks = []

        products += await asyncio.gather(*tasks)

        matched, unmatched = await self.find_similar_to_article(article=main_article, products=products)
        return matched, unmatched

    @staticmethod
    async def remove_duplicate_nms(products):
        unique = []
        checked = []
        for product in products:
            article = product['card']['nm_id']
            # article = product['article wb']

            if article not in checked:
                unique.append(product)
                checked.append(article)
        return unique

    async def aggregate_data_management(self):
        products = await self.match_utils.get_products()
        prepared_for_saving_products = await self.match_utils.prepare_wb_products_for_saving(products=products)
        await self.product_queries.save_in_db(instances=prepared_for_saving_products, many=True)
