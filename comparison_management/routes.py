import io

import pandas as pd
from fastapi import APIRouter, File
from starlette.responses import StreamingResponse

from comparison_management.services import CMServices
from match_management.xlsx_utils import XlsxUtils

router = APIRouter(prefix='/compare-management', tags=['Utils (comparison, other..)'])


xlsx_utils = XlsxUtils()
cm_services = CMServices()


@router.get('/get-characteristics/{article_wb}/')
async def get_characteristics(article_wb: int):
    characteristics = await cm_services.chars_management(article_wb=article_wb)

    df = pd.DataFrame(characteristics).T

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()

    return StreamingResponse(io.BytesIO(output.getvalue()),
                             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={'Content-Disposition': f'attachment; filename="characteristics.xlsx"'})


@router.get('/get-not-profitable-products/')
async def get_not_profitable_products():
    cached_files = await cm_services.not_profitable_management()
    return xlsx_utils.zip_response(filenames=cached_files, zip_filename='not-profitable-products.zip')


@router.get('/get-not-profitable-products/{brand_id}/')
async def get_not_profitable_products_by_brand_id(brand_id: int):
    cached_files = await cm_services.not_profitable_management(brand_id=brand_id)
    return xlsx_utils.zip_response(
        filenames=cached_files, zip_filename=f'not-profitable-products_by_brand_id {brand_id}.zip')


@router.get('/get-recommended-min-price/')
async def get_recommended_min_price():
    sequence = await cm_services.get_recommended_min_prices()
    return xlsx_utils.streaming_response(sequence=sequence, file_name='Recommended_min_prices')


@router.get('/get-profitable-products/{brand_id}/')
async def get_profitable_products(brand_id: int):
    cached_files = await cm_services.profitable_management(brand_id=brand_id)
    return xlsx_utils.zip_response(filenames=cached_files, zip_filename='profitable-products.zip')


@router.get('/get-child-less-than-three/')
async def get_child_less_then_three():
    cached_files = await cm_services.get_child_less_than_three()
    return xlsx_utils.zip_response(filenames=cached_files, zip_filename='less_than_tree.zip')


@router.post('/get-children-by-articles-wb/')
async def get_children_by_articles(file: bytes = File()):
    df = pd.read_excel(file)
    cached_files = await cm_services.get_children_by_articles_wb(df=df)
    return xlsx_utils.zip_response(filenames=cached_files, zip_filename='child_products.zip')


@router.post('/get-non-existent-articles/')
async def get_non_existent_articles(file: bytes = File()):
    df = pd.read_excel(file)
    data = await cm_services.get_non_existent_articles(df=df)

    df = pd.DataFrame(data)

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()

    return StreamingResponse(io.BytesIO(output.getvalue()),
                             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={'Content-Disposition': f'attachment; filename="non_existent_products.xlsx"'})
