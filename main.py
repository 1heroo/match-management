import json

import uvicorn
from db.db import async_engine
from fastapi import FastAPI
from sqladmin import Admin

from match_management.admin import ProductAdmin, MatchedProductAdmin, ChildMatchedProductAdmin, BrandAdmin
from match_management.routes import router as mm_router
from price_management.routes import router as pm_router


app = FastAPI(title='Сопоставление товаров и динамическое управление ценой')


# routes staff
app.include_router(mm_router)
app.include_router(pm_router)

# admin staff
admin = Admin(app, async_engine)

admin.add_view(ProductAdmin)
admin.add_view(MatchedProductAdmin)
admin.add_view(ChildMatchedProductAdmin)
admin.add_view(BrandAdmin)

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )
