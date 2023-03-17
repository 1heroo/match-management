from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from match_management.queries import MatchedProductQueries, ChildMatchedProductQueries

router = APIRouter(prefix='/api/v1/matched-product', tags=['API'])


matched_product_queries = MatchedProductQueries()
child_matched_product_queries = ChildMatchedProductQueries()


@router.get('/{article_wb}/get-matches/')
async def get_matched(article_wb: int):
    matched_product = await matched_product_queries.get_product_by_nm(nm=article_wb)

    if matched_product is None:
        return JSONResponse(content={'message': 'article not found'}, status_code=status.HTTP_404_NOT_FOUND)

    child_matched_product = await child_matched_product_queries.get_children_by_parent_nm_id(
        parent_nm_id=matched_product.nm_id)

    return JSONResponse(content={
        'product_nm_id': matched_product.nm_id,
        'children': [child_product.nm_id for child_product in child_matched_product]
    }, status_code=status.HTTP_200_OK)
