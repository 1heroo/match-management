from db.db import async_session
from db.queries import BaseQueries
from match_management.models import Product, MatchedProduct, ChildMatchedProduct, Brand
import sqlalchemy as sa


class ProductQueries(BaseQueries):

    model = Product

    async def get_all_unmatched_products(self):
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
                product = saved_matched_product

        if not product:
            product = the_product
        await self.save_in_db(instances=product)
        return product


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

class BrandQueries(BaseQueries):

    model = Brand

    async def fetch_all(self):
        async with async_session() as session:
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