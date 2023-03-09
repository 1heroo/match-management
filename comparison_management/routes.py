import io

import pandas as pd
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from comparison_management.services import CMServices

router = APIRouter(prefix='/compare-management', tags=['Compare management'])

cm_services = CMServices()


@router.get('/get-characteristics/{article_wb}/')
async def get_characteristics(article_wb: int):
    characteristics = await cm_services.chars_management(article_wb=article_wb)

    df = pd.DataFrame(characteristics).T

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer)
    writer.save()

    return StreamingResponse(io.BytesIO(output.getvalue()),
                             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={'Content-Disposition': f'attachment; filename="characteristics.xlsx"'})


