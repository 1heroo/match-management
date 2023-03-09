from fastapi import APIRouter

from comparison_management.services import CMServices

router = APIRouter(prefix='/compare-management', tags=['compare-management'])

cm_services = CMServices()


# @router.get('/get-characteristics/{article_wb}/')
# async def get_characteristics(article_wb: int):
#     characteristics = await cm_services.chars_management(article_wb=article_wb)

