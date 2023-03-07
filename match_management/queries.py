from db.db import async_session
from db.queries import BaseQueries
from match_management.models import Product, MatchedProduct, ChildMatchedProduct
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

    async def save_or_update(self, matched_products):
        saved_matched_products = await self.fetch_all()
        all_nms = [saved_matched_product.nm_id for saved_matched_product in saved_matched_products]
        new_instances = [matched_product for matched_product in matched_products if matched_product.nm_id not in all_nms]
        db_instances = []

        for saved_matched_product in saved_matched_products:
            for matched_product in matched_products:
                if saved_matched_product.nm_id == matched_product.nm_id:
                    saved_matched_product.min_price = matched_product.min_price
                    db_instances.append(saved_matched_product)

        await self.save_in_db(instances=db_instances + new_instances, many=True)


class ChildMatchedProductQueries(BaseQueries):

    model = ChildMatchedProduct

