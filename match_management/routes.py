import asyncio
import io
import os
import time

from fastapi import APIRouter, File
import pandas as pd
from starlette import status
from starlette.responses import StreamingResponse, Response

from match_management.queries import ProductQueries, ChildMatchedProductQueries, MatchedProductQueries, BrandQueries
from match_management.services import MatchServices
from match_management.utils import MatchUtils
import glob

from match_management.xlsx_utils import XlsxUtils

router = APIRouter(prefix='/mm', tags=['Match management'])

matched_services = MatchServices()
matched_queries = MatchedProductQueries()
match_utils = MatchUtils()

child_matched_queries = ChildMatchedProductQueries()
product_queries = ProductQueries()
brand_queries = BrandQueries()
xlsx_utils = XlsxUtils()


@router.get('/lunch-matching-with_local_file/')
async def launch_matching_with_files():
    products = [product.product for product in await product_queries.fetch_all()]

    for product_file in glob.glob('file_db/*.xlsx'):
        df = pd.read_excel(product_file)
        article_column = df['Артикул WB'].name
        min_price_column = df['Минимальная цена'].name
        await matched_services.find_matches(
            df=df, article_column=article_column, min_price_column=min_price_column, products=products)

    return Response(status_code=status.HTTP_200_OK)


@router.post('/launch-matching/')
async def main(file: bytes = File()):
    nms = [product.nm_id for product in await product_queries.fetch_all()]
    products = await match_utils.get_detail_by_nms(nms=nms)

    df = pd.read_excel(file)
    article_column = df['Артикул WB'].name
    min_price_column = df['Минимальная цена'].name
    await matched_services.find_matches(
        df=df, article_column=article_column, min_price_column=min_price_column, products=products)
    return Response(status_code=status.HTTP_200_OK)


@router.get('/aggregate-products/')
async def aggregate_products():
    brands = await brand_queries.fetch_all(included_to_pm=True)
    brand_ids = [brand.brand_id for brand in brands]
    await matched_services.aggregate_data_management(brand_ids=brand_ids)
    return Response(status_code=status.HTTP_200_OK)


@router.get('/get-child-matched-products/{article_wb}/')
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


@router.get('/get-products-with-no-children/')
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


@router.post('/import-manually-matched-products/')
async def import_matched_products(file: bytes = File()):
    df = pd.read_excel(file)

    the_product_column = df['Наш Артикул WB'].name
    child_product_column = df['Сопоставленный Артикул WB'].name
    await matched_services.manually_add_child_matches(
        df=df, the_product_column=the_product_column, child_product_column=child_product_column)

    return Response(status_code=status.HTTP_200_OK)


@router.post('/import-rrc/')
async def import_rrc(sheet_name: str = None, file: bytes = File()):
    sheet_name = 0 if sheet_name is None else sheet_name

    file_name = str(int(time.time())) + '.csv'

    df = pd.read_excel(file, sheet_name=sheet_name, header=None)
    df = xlsx_utils.handle_xlsx(df=df, file_name=file_name)

    article_column = xlsx_utils.find_article_column(df=df)
    price_column = xlsx_utils.find_price_column(df=df)
    print(article_column, price_column)
    if price_column is None or article_column is None:
        return False

    await matched_services.import_rrc(df=df, price_column=price_column, article_column=article_column)
    os.remove(file_name)

    return Response(status_code=status.HTTP_200_OK)


# @router.get('/')
async def maina():

    products = await match_utils.get_all_catalogs_from_brand(brand_ids=[
        25609,
        36933,
    ])
    all_ids = [item.get('id') for item in products]

    # all_ids = all_ids[:5] + all_ids[-5:]
    details = await match_utils.get_detail_by_nms(nms=all_ids)

    categories_brand_1 = []
    categories_brand_2 = []

    unique_details_brand_1 = []
    unique_details_brand_2 = []

    for product in details:
        category = product['card'].get('subj_name')
        brand_id = product['detail'].get('brandId')
        if brand_id == 25609:
            if category not in categories_brand_1:
                categories_brand_1.append(category)
                unique_details_brand_1.append(product)
        else:
            if category not in categories_brand_2:
                categories_brand_2.append(category)
                unique_details_brand_2.append(product)

    output_data_1 = []
    output_data_2 = []
    for detail in unique_details_brand_1:
        extended = detail['detail'].get('extended')

        if not extended:
            continue

        output_data_1.append({
            'Категория': None,
            'Подкатегория': detail['card'].get('subj_root_name'),
            'Подкатегория2': detail['card'].get('subj_name'),
            'STURM "brandId": 25609': extended.get('clientSale')
        })
    for detail in unique_details_brand_2:
        extended = detail['detail'].get('extended')

        if not extended:
            continue

        output_data_2.append({
            'Категория': None,
            'Подкатегория': detail['card'].get('subj_root_name'),
            'Подкатегория2': detail['card'].get('subj_name'),
            'STURM "brandId": 36933': extended.get('clientSale')
        })
    df1 = pd.DataFrame(output_data_1)
    df2 = pd.DataFrame(output_data_2)

    df = pd.merge(df1, df2, how='outer', left_on=['Подкатегория', 'Подкатегория2'], right_on=['Подкатегория', 'Подкатегория2'])
    df = df.drop('Категория_y', axis=1)

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()

    return StreamingResponse(io.BytesIO(output.getvalue()),
                             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={'Content-Disposition': f'attachment; filename="characteristics.xlsx"'})