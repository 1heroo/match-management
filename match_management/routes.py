import io

from fastapi import APIRouter, File
import pandas as pd
from starlette import status
from starlette.responses import StreamingResponse, Response

from match_management.queries import ProductQueries, ChildMatchedProductQueries, MatchedProductQueries
from match_management.services import MatchServices
from match_management.utils import MatchUtils

router = APIRouter(prefix='/mm', tags=['match management'])

matched_services = MatchServices()
matched_queries = MatchedProductQueries()
match_utils = MatchUtils()

child_matched_queries = ChildMatchedProductQueries()
product_queries = ProductQueries()


@router.post('/launch-matching')
async def main(file: bytes = File()):
    df = pd.read_excel(file)
    article_column = df['Артикул WB'].name
    min_price_column = df['Минимальная цена'].name
    await matched_services.find_matches(df=df, article_column=article_column, min_price_column=min_price_column)
    return Response(status_code=status.HTTP_200_OK)


@router.get('/aggregate-products/')
async def aggregate_products():
    await matched_services.aggregate_data_management()
    return Response(status_code=status.HTTP_200_OK)


@router.get('/get-child-matched-products/{article_wb}')
async def get_child_matched_products(article_wb: int):
    child_matched_products = await child_matched_queries.get_children_by_parent_nm_id(parent_nm_id=article_wb)

    products = await match_utils.prepare_output(products=child_matched_products)

    products = sorted(products, key=lambda item: item.get('price'))
    df = pd.DataFrame(products)

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()

    return StreamingResponse(io.BytesIO(output.getvalue()),
                             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={'Content-Disposition': f'attachment; filename="{article_wb}.xlsx"'})


@router.post('/remove-from-child-matched-products/')
async def remove_from_matched_products(file: bytes = File()):
    df = pd.read_excel(file)
    await matched_services.remove_from_child_matched_products(df=df)

    return Response(status_code=status.HTTP_200_OK)
