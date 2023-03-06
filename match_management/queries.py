from db.db import async_session
from db.queries import BaseQueries
from match_management.models import Product, MatchedProduct
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

    async def get_all_matched(self):
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
