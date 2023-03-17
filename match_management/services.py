import asyncio

import pandas as pd

from core.settings import settings
from match_management.queries import ProductQueries, MatchedProductQueries, ChildMatchedProductQueries
from match_management.utils import MatchUtils
from match_management.models import MatchedProduct
from price_management.services import PMServices


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
    def extra_filter(the_product, matched):
        return [
            matched_product for matched_product in matched if matched_product.nm_id not in the_product.checked_nms.get('checked_nms')
        ]


class MatchServices:

    def __init__(self):
        self.match_utils = MatchUtils()
        self.filter_lvl = FilterLevels()
        self.product_queries = ProductQueries()
        self.matched_product_queries = MatchedProductQueries()
        self.child_matched_product_queries = ChildMatchedProductQueries()
        self.pm_services = PMServices()

    async def find_matches(self, df, article_column, min_price_column, products):

        # df[min_price_column] = df[min_price_column].isnull()

        print(df)
        for index in df.index:
            article = int(df[article_column][index])

            try:
                min_price = int(df[min_price_column][index])
            except:
                continue

            print(article)

            the_product, matched = await self.match_management(article=article, products=products)

            the_product = await self.match_utils.prepare_matched_product(the_product=the_product, min_price=min_price)
            the_product = await self.matched_product_queries.save_or_update(the_product=the_product)

            matched_products = await self.match_utils.prepare_child_matched_products(
                child_matched_products=matched, the_product=the_product)

            # extra_filter
            matched_products = self.filter_lvl.extra_filter(the_product=the_product, matched=matched_products)
            await self.child_matched_product_queries.get_or_create(child_matched_products=matched_products)

            await self.product_queries.delete_by_nms([
                product['card'].get('nm_id') for product in matched
            ])

    async def match_management(self, article, products):
        _, matched = await self.find_similar_to_article(article=article, products=products)

        the_product, matched_by_wb_recs = await self.check_by_identical_nms(matched=matched, main_article=article)
        matched = await self.remove_duplicate_nms(products=matched + matched_by_wb_recs)

        return the_product, matched

    async def find_similar_to_article(self, article, products=None):
        the_product = await self.match_utils.get_product_data(article=article)

        output_data = []

        products = await self.match_utils.check_stocks(products=products)

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
            identical = await self.match_utils.get_identical(article=product['card']['nm_id'])
            if identical:
                identical_nms += identical

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

            if article not in checked:
                unique.append(product)
                checked.append(article)
        return unique

    async def aggregate_data_management(self, brand_ids):
        products = await self.match_utils.get_products(brand_ids)
        prepared_for_saving_products = await self.match_utils.prepare_wb_products_for_saving(products=products)
        await self.product_queries.save_or_update(products=prepared_for_saving_products)

    async def remove_from_child_matched_products(self, df: pd.DataFrame):
        wb_standard_auth = self.pm_services.wb_api_utils.api_auth(token=settings.WB_STANDARD_API_TOKEN)

        the_product = None
        for index in df.index:
            nm_id = df['article wb'][index]
            child_matched_product = await self.child_matched_product_queries.get_child_by_nm_id(nm_id=nm_id)

            if child_matched_product is not None:
                the_product = await self.matched_product_queries.get_product_by_nm(
                    nm=child_matched_product.parent_nm_id)
                break

        if the_product is None:
            return

        unmatched_products_to_be_saved = []

        for index in df.index:
            child_matched_product = await self.child_matched_product_queries.get_child_by_nm_id(
                nm_id=df['article wb'][index])
            if child_matched_product:
                unmatched_products_to_be_saved.append(child_matched_product.product)
                await self.child_matched_product_queries.delete_instance(instance=child_matched_product)

        prepared_for_saving_products = await self.match_utils.prepare_wb_products_for_saving(
            products=unmatched_products_to_be_saved)
        print(prepared_for_saving_products)
        checked_nms = [product.nm_id for product in prepared_for_saving_products]

        await self.pm_services.update_price(the_product=the_product, wb_standard_auth=wb_standard_auth)
        await self.product_queries.save_in_db(instances=prepared_for_saving_products, many=True)
        await self.matched_product_queries.update_checked(nm_id=the_product.nm_id, checked_nms=checked_nms)

    async def get_products_with_no_children(self):
        matched_products = await self.matched_product_queries.fetch_all()
        matched_products_with_children = await self.matched_product_queries.get_matched_products_with_children()

        matched_products = [product for product in matched_products if product.nm_id not in
                            [matched_product_with_children.nm_id for matched_product_with_children in matched_products_with_children]]
        products = await self.match_utils.prepare_output(products=matched_products, the_product=True)
        return products

    async def manually_add_child_matches(self, df, the_product_column, child_product_column):

        wb_standard_auth = self.pm_services.wb_api_utils.api_auth(settings.WB_STANDARD_API_TOKEN)

        products_to_be_imported = await self.match_utils.get_detail_by_nms(
            nms=[int(df[child_product_column][index]) for index in df.index])

        products_to_be_imported = [
            {'child_nm_id': product['card'].get('nm_id'), 'product': product}
            for product in products_to_be_imported]

        df = pd.merge(
            df, pd.DataFrame(products_to_be_imported), how='inner', left_on=child_product_column, right_on='child_nm_id')

        nms_to_be_removed_from_unmatched_products = []
        children_to_be_saved = []

        for index in df.index:
            the_product_nm = int(df[the_product_column][index])
            the_product = await self.matched_product_queries.get_product_by_nm(nm=the_product_nm)

            if the_product is None:
                print('the product not found')
                continue
            child = await self.match_utils.prepare_child_matched_products(
                the_product=the_product, child_matched_products=[df['product'][index]])

            children_to_be_saved += child
            await self.child_matched_product_queries.resave_matched_product(
                the_product=the_product, matched_products=child)

            nms_to_be_removed_from_unmatched_products.append(int(df[child_product_column][index]))
            await self.pm_services.update_price(the_product=the_product, wb_standard_auth=wb_standard_auth)

        await self.child_matched_product_queries.get_or_create(child_matched_products=children_to_be_saved)
        await self.product_queries.delete_by_nms(nms=nms_to_be_removed_from_unmatched_products)
