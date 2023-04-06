import json

import pandas as pd

from db.db import async_session
from db.queries import BaseQueries
from match_management.models import Product, MatchedProduct, ChildMatchedProduct, Brand
import sqlalchemy as sa


class MatchedProductQueries(BaseQueries):
    model = MatchedProduct

    async def fetch_all(self):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model)
            )
            return result.scalars().all()

    async def get_product_by_nm(self, nm):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model).where(self.model.nm_id == nm)
            )
            return result.scalars().first()

    async def save_or_update(self, the_product):
        product = None
        saved_matched_products = await self.fetch_all()
        for saved_matched_product in saved_matched_products:
            if the_product.nm_id == saved_matched_product.nm_id:
                saved_matched_product.min_price = the_product.min_price
                saved_matched_product.the_product = the_product.the_product
                product = saved_matched_product

        if product is None:
            product = the_product
        await self.save_in_db(instances=product)
        return product

    async def update_checked(self, nm_id, checked_nms):
        the_product = await self.get_product_by_nm(nm=nm_id)
        if the_product is None:
            return

        saved_checked_nms = the_product.checked_nms.get('checked_nms')
        the_product.checked_nms = {'checked_nms': saved_checked_nms + checked_nms}
        await self.save_in_db(instances=the_product)

    async def get_matched_products_with_children(self):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model).where(self.model.matched_products)
            )
            return result.scalars().all()

    async def get_matched_products_by_brand_id(self, brand_id):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model).where(self.model.brand_id == brand_id)
            )
            return result.scalars().all()


class ChildMatchedProductQueries(BaseQueries):
    model = ChildMatchedProduct

    async def fetch_all(self):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model)
            )
            return result.scalars().all()

    async def get_or_create(self, child_matched_products):
        saved_child_matched_products = await self.fetch_all()
        all_nms = [saved_child_matched_product.nm_id for saved_child_matched_product in saved_child_matched_products]
        to_be_saved = [child_matched_product for child_matched_product in child_matched_products
                       if child_matched_product.nm_id not in all_nms]
        await self.save_in_db(instances=to_be_saved, many=True)

    async def get_children_by_parent_id(self, parent_id):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model).where(self.model.parent_id == parent_id)
            )
            return result.scalars().all()

    async def get_children_by_parent_nm_id(self, parent_nm_id):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model).where(self.model.parent_nm_id == parent_nm_id)
            )
            return result.scalars().all()

    async def get_child_by_nm_id(self, nm_id):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model).where(self.model.nm_id == nm_id)
            )
            return result.scalars().first()

    async def resave_matched_product(self, the_product, matched_products):
        saved_child_matched_products = await self.fetch_all()
        instances_to_be_resaved = []

        for saved_child in saved_child_matched_products:
            for matched_product in matched_products:
                if saved_child.nm_id == matched_product.nm_id:
                    saved_child.parent_nm_id = the_product.nm_id
                    saved_child.parent_id = the_product.id
                    instances_to_be_resaved.append(saved_child)

        await self.save_in_db(instances=instances_to_be_resaved, many=True)


class ProductQueries(BaseQueries):
    model = Product
    matched_product_queries = MatchedProductQueries()
    child_matched_product_queries = ChildMatchedProductQueries()

    async def fetch_all(self):
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model)
            )
            return result.scalars().all()

    async def delete_by_nms(self, nms):

        async with async_session() as session:
            for nm in nms:
                instance = await session.execute(
                    sa.select(self.model).where(self.model.nm_id == int(nm))
                )
                instance = instance.scalars().first()
                if instance:
                    await session.delete(instance)
                    await session.commit()

    async def get_or_create(self, products):
        unmatched_products = await self.fetch_all()
        child_matched_products = await self.child_matched_product_queries.fetch_all()
        all_nms = [product.nm_id for product in unmatched_products] \
                  + [matched_product.nm_id for matched_product in child_matched_products]

        to_be_saved = [product for product in products
                       if product.nm_id not in all_nms]

        await self.save_in_db(instances=to_be_saved, many=True)

    async def save_or_update(self, products):
        db_instances = []
        all_saved_products = await self.fetch_all() \
                             + await self.matched_product_queries.fetch_all() \
                             + await self.child_matched_product_queries.fetch_all()

        all_nms = [product.nm_id for product in all_saved_products]
        new_instances = [product for product in products if product.nm_id not in all_nms]

        products = [{'nm_id': product.nm_id, 'new_product': product} for product in products]
        saved_products = [{'nm_id': product.nm_id, 'saved_product': product} for product in all_saved_products]

        products_df = pd.DataFrame(products)
        saved_products_df = pd.DataFrame(saved_products)
        df = pd.merge(
            saved_products_df, products_df, how='inner', left_on='nm_id', right_on='nm_id')

        for index in df.index:
            saved_product = df['saved_product'][index]
            new_product = df['new_product'][index]

            price = new_product.product['detail'].get('salePriceU')
            if price:
                price //= 100

            if isinstance(saved_product, Product):
                saved_product.product = new_product.product
            elif isinstance(saved_product, MatchedProduct):
                saved_product.price = price
                saved_product.the_product = new_product.product
            elif isinstance(saved_product, ChildMatchedProduct):
                saved_product.price = price
                saved_product.product = new_product.product
            db_instances.append(saved_product)

        await self.save_in_db(instances=new_instances + db_instances, many=True)


class BrandQueries(BaseQueries):
    model = Brand

    async def fetch_all(self, included_to_pm=False):
        async with async_session() as session:
            if included_to_pm:
                result = await session.execute(
                    sa.select(self.model).where(self.model.is_included_to_pm)
                )
            else:
                result = await session.execute(
                    sa.select(self.model)
                )
            return result.scalars().all()

    async def get_brand_by_brand_id(self, brand_id, included_to_pm=False):
        async with async_session() as session:
            if included_to_pm:
                result = await session.execute(
                    sa.select(self.model).where(self.model.brand_id == brand_id).where(self.model.is_included_to_pm)
                )
            else:
                result = await session.execute(
                    sa.select(self.model).where(self.model.brand_id == brand_id)
                )
            return result.scalars().first()
