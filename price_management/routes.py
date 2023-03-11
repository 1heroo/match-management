from fastapi import APIRouter
from fastapi.openapi.models import Response
from starlette import status

from price_management.services import PMServices


router = APIRouter(prefix='/price', tags=['Price Management'])
pm_services = PMServices()


@router.get('/price-monitoring/')
async def price_management():
    await pm_services.price_management()
    return Response(status_code=status.HTTP_200_OK)
