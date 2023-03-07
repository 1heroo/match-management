import io

import pandas as pd
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from price_management.services import PMServices


router = APIRouter(prefix='/price', tags=['Price Management'])
pm_services = PMServices()


@router.get('/price-monitoring')
async def price_management():
    item = await pm_services.price_management()
    return True
    # df = pd.DataFrame([item])
    #
    # output = io.BytesIO()
    # writer = pd.ExcelWriter(output, engine='xlsxwriter')
    # df.to_excel(writer, index=False)
    # writer.save()
    #
    # return StreamingResponse(io.BytesIO(output.getvalue()),
    #                          media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #                          headers={'Content-Disposition': f'attachment; filename="calculated_price.xlsx"'})

