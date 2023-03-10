import io

from fastapi import APIRouter, File
import pandas as pd
from starlette import status
from starlette.responses import StreamingResponse, Response

from match_management.queries import ProductQueries, ChildMatchedProductQueries, MatchedProductQueries, BrandQueries
from match_management.services import MatchServices
from match_management.utils import MatchUtils
import glob


router = APIRouter(prefix='/mm', tags=['Match management'])

matched_services = MatchServices()
matched_queries = MatchedProductQueries()
match_utils = MatchUtils()

child_matched_queries = ChildMatchedProductQueries()
product_queries = ProductQueries()
brand_queries = BrandQueries()


@router.get('/lunch-matching-with_local_file/')
async def launch_matching_with_files():
    nms = [product.nm_id for product in await product_queries.fetch_all()]
    products = await match_utils.get_detail_by_nms(nms=nms)

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
