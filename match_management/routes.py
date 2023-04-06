import asyncio
import io
import os
import time

from fastapi import APIRouter, File
import pandas as pd
from starlette import status
from starlette.responses import StreamingResponse, Response, JSONResponse

from match_management.queries import ProductQueries, ChildMatchedProductQueries, MatchedProductQueries, BrandQueries
from match_management.services import MatchServices
from match_management.utils import MatchUtils
import glob

from match_management.xlsx_utils import XlsxUtils

router = APIRouter(prefix='/match-management')

matched_services = MatchServices()
matched_queries = MatchedProductQueries()
match_utils = MatchUtils()

child_matched_queries = ChildMatchedProductQueries()
product_queries = ProductQueries()
brand_queries = BrandQueries()
xlsx_utils = XlsxUtils()


@router.get('/launch-matching/', tags=['wb interactions'])
async def launch_matching():
    products = [product.product for product in await product_queries.fetch_all()]

    await matched_services.find_matches(products=products)
    return Response(status_code=status.HTTP_200_OK)


@router.get('/aggregate-products/', tags=['wb interactions'])
async def aggregate_products():
    brands = await brand_queries.fetch_all(included_to_pm=True)
    brand_ids = [brand.brand_id for brand in brands]
    await matched_services.aggregate_data_management(brand_ids=brand_ids)
    return Response(status_code=status.HTTP_200_OK)


@router.post('/import-my-products/', tags=['database interactions'])
async def import_my_products(sheet_name: str = None, file: bytes = File()):
    sheet_name = 0 if sheet_name is None else sheet_name
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)
    file_name = str(int(time.time())) + '.csv'
    df = xlsx_utils.handle_xlsx(df=df, file_name=file_name)

    article_column = xlsx_utils.find_article_column(df=df)
    price_column = xlsx_utils.find_min_price_column(df=df)
    print(article_column, price_column)
    if price_column is None or article_column is None:
        return JSONResponse(content={'message': 'Не правильная струкутра в экзель'},
                            status_code=status.HTTP_400_BAD_REQUEST)

    await matched_services.import_my_products(df=df, price_column=price_column, article_column=article_column)
    os.remove(file_name)

    return Response(status_code=status.HTTP_200_OK)


@router.post('/import-rrc/', tags=['database interactions'])
async def import_rrc(sheet_name: str = None, file: bytes = File()):
    sheet_name = 0 if sheet_name is None else sheet_name

    file_name = str(int(time.time())) + '.csv'

    df = pd.read_excel(file, sheet_name=sheet_name, header=None)
    df = xlsx_utils.handle_xlsx(df=df, file_name=file_name)

    article_column = xlsx_utils.find_article_column(df=df)
    price_column = xlsx_utils.find_price_column(df=df)
    print(article_column, price_column)
    if price_column is None or article_column is None:
        return JSONResponse(content={'message': 'Не правильная струкутра в экзель'},
                            status_code=status.HTTP_400_BAD_REQUEST)

    await matched_services.import_rrc(df=df, price_column=price_column, article_column=article_column)
    os.remove(file_name)

    return Response(status_code=status.HTTP_200_OK)


@router.post('/import-min-prices/', tags=['database interactions'])
async def import_min_prices(sheet_name: str = None, file: bytes = File()):
    sheet_name = 0 if sheet_name is None else sheet_name
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)
    file_name = str(int(time.time())) + '.csv'
    df = xlsx_utils.handle_xlsx(df=df, file_name=file_name)

    article_column = xlsx_utils.find_article_column(df=df)
    price_column = xlsx_utils.find_min_price_column(df=df)
    if price_column is None or article_column is None:
        return JSONResponse(content={'message': 'Не правильная струкутра в экзель'},
                            status_code=status.HTTP_400_BAD_REQUEST)

    await matched_services.import_min_price(df=df, price_column=price_column, article_column=article_column)
    os.remove(file_name)

    return Response(status_code=status.HTTP_200_OK)


@router.post('/import-manually-matched-products/', tags=['database interactions'])
async def import_matched_products(file: bytes = File()):
    df = pd.read_excel(file)

    the_product_column = df['Наш Артикул WB'].name
    child_product_column = df['Сопоставленный Артикул WB'].name
    await matched_services.manually_add_child_matches(
        df=df, the_product_column=the_product_column, child_product_column=child_product_column)

    return Response(status_code=status.HTTP_200_OK)


@router.get('/get-child-matched-products/{article_wb}/', tags=['match product utils'])
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


@router.post('/remove-from-child-matched-products/', tags=['match product utils'])
async def remove_from_matched_products(file: bytes = File()):
    df = pd.read_excel(file)
    await matched_services.remove_from_child_matched_products(df=df)

    return Response(status_code=status.HTTP_200_OK)


@router.get('/get-products-with-no-children/', tags=['match product utils'])
async def get_products_with_no_children():
    products = await matched_services.get_products_with_no_children()
    df = pd.DataFrame(products)

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()

    return StreamingResponse(io.BytesIO(output.getvalue()),
                             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={'Content-Disposition': f'attachment; filename="no_children_products.xlsx"'})

