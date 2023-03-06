import io

from fastapi import APIRouter, File
import pandas as pd
from starlette.responses import StreamingResponse

from match_management.queries import ProductQueries
from match_management.services import MatchServices

router = APIRouter(prefix='/mm')

match_services = MatchServices()
product_queries = ProductQueries()


@router.post('/launch-matching')
async def main(file: bytes = File()):
    df = pd.read_excel(file)
    article_column = df['Номенклатура'].name
    min_price_column = df['Минимальная цена'].name
    await match_services.find_matches(df=df, article_column=article_column, min_price_column=min_price_column)
    return

    # _, matched = await match_services.match_management(article=81865158)

    # df = pd.DataFrame(matched)
    #
    # output = io.BytesIO()
    # writer = pd.ExcelWriter(output, engine='xlsxwriter')
    # df.to_excel(writer, index=False)
    # writer.save()
    #
    # return StreamingResponse(io.BytesIO(output.getvalue()),
    #                          media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #                          headers={'Content-Disposition': f'attachment; filename="81865158.xlsx"'})


@router.get('/aggregate-products/')
async def aggregate_products():
    await match_services.aggregate_data_management()
    return None
