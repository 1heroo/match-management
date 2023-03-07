import asyncio
import json
from match_management.models import Product, MatchedProduct, ChildMatchedProduct
import aiohttp


class MatchUtils:

    def __init__(self):
        pass

    @staticmethod
    async def make_get_request(url, headers):
        async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
            response = await session.get(url=url)
            if response.status == 200:
                return json.loads(await response.text())

    async def get_catalog(self, url):
        products = []

        for page in range(1, 101):
            print(page, 'catalog page')
            page_url = url.format(page=page)
            data = await self.make_get_request(page_url, headers={})
            data = data['data']['products']
            products += data
            if len(data) != 100:
                break

        return products

    async def get_exact_category(self):
        url = 'https://catalog.wb.ru/catalog/garden6/catalog?appType=1&cat=128824&couponsGeo=12,3,18,15,21&curr=rub&dest=-1257786&emp=0&fbrand=15489&lang=ru&locale=ru&page={page}&pricemarginCoeff=1.0&reg=0&regions=80,64,38,4,83,33,68,70,69,30,86,75,40,1,22,66,31,48,110,71&sort=popular&spp=0'
        products = await self.get_catalog(url=url)
        return products

    async def get_all_catalogs_from_brand(self, brand_ids):
        products = []
        for brand_id in brand_ids:
            url = 'https://catalog.wb.ru/brands/h/catalog?appType=1&brand=%s&couponsGeo=12,3,18,15,21&curr=rub&dest=-455203&emp=0&lang=ru&locale=ru&page={page}&pricemarginCoeff=1.0&reg=1&regions=80,64,38,4,83,33,68,70,69,30,86,75,40,1,66,31,48,110,22,71&sort=popular&spp=27&sppFixGeo=4' % brand_id
            print(brand_id)
            products += await self.get_catalog(url=url)
        return products

    async def get_product_data(self, article):
        card_url = make_head(int(article)) + make_tail(str(article), 'ru/card.json')
        obj = {}
        card = await self.make_get_request(url=card_url, headers={})

        detail_url = f'https://card.wb.ru/cards/detail?spp=27&regions=80,64,38,4,83,33,68,70,69,30,86,75,40,1,22,66,31,48,110,71&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&sppFixGeo=4&dest=-455203&nm={article}'
        detail = await self.make_get_request(detail_url, headers={})

        if detail:
            detail = detail['data']['products']
        else:
            detail = {}

        seller_url = make_head(int(article)) + make_tail(str(article), 'sellers.json')
        seller_data = await self.make_get_request(seller_url, headers={})

        obj.update({
            'card': card if card else {},
            'detail': detail[0] if detail else {},
            'seller': seller_data if seller_data else {}
        })

        return obj

    async def get_products(self):
        # products = await self.get_exact_category()136360
        '136360, 15489, 15490, 15488'
        products = await self.get_all_catalogs_from_brand(brand_ids=[234082])
        output_data = []

        tasks = []
        count = 1

        for product in products:
            task = asyncio.create_task(self.get_product_data(article=product.get('id')))
            tasks.append(task)
            count += 1

            if count % 50 == 0:
                print(count, 'product data')
                output_data += await asyncio.gather(*tasks, return_exceptions=True)
                tasks = []

        output_data += await asyncio.gather(*tasks, return_exceptions=True)
        output_data = [item for item in output_data if not isinstance(item, Exception) and item]
        return output_data

    async def get_detail_by_nms(self, nms):
        output_data = []
        tasks = []
        count = 1

        for nm in nms:
            task = asyncio.create_task(self.get_product_data(article=nm))
            tasks.append(task)
            count += 1

            if count % 50 == 0:
                print(count, 'product data')
                output_data += await asyncio.gather(*tasks, return_exceptions=True)
                tasks = []

        output_data += await asyncio.gather(*tasks, return_exceptions=True)
        output_data = [item for item in output_data if not isinstance(item, Exception) and item]
        return output_data


    async def get_identical(self, article):
        url = f'https://identical-products.wildberries.ru/api/v1/identical?nmID={article}'
        return await self.make_get_request(url=url, headers={})

    async def get_in_visual_similar(self, article):
        url = f'https://in-visual-similar.wildberries.ru/?nm={article}'
        return await self.make_get_request(url=url, headers={})

    async def get_in_search(self, query):
        url = 'https://search-goods.wildberries.ru/search?query={query}'
        return await self.make_get_request(url=url, headers={})

    @staticmethod
    async def prepare_output(products, by_matching=False):
        output_data = []
        for product in products:
            obj = {
                'vendorCode': product['card']['vendor_code'],
                'name': product['card'].get('imt_name'),
                'article wb': product['card']['nm_id'],
                'price': int(product['detail'].get('salePriceU')) // 100,
                'vendor': product['seller']['supplierName'],
                'link': f"https://www.wildberries.ru/catalog/{product['card']['nm_id']}/detail.aspx?targetUrl=GP",
                # 'by matching': by_matching
            }

            output_data.append(obj)
        return output_data

    @staticmethod
    async def prepare_wb_products_for_saving(products):
        output_data = []
        for product in products:
            output_data.append(Product(
                nm_id=product['card']['nm_id'],
                product=product
            ))
        return output_data

    @staticmethod
    async def prepare_matched_product(the_product, min_price):
        the_product_to_be_saved = MatchedProduct(
            nm_id=the_product['card'].get('nm_id'),
            title=the_product['card'].get('imt_name'),
            subj_name=the_product['card'].get('subj_name'),
            subj_root_name=the_product['card'].get('subj_root_name'),
            vendor_code=the_product['card'].get('vendor_code'),
            min_price=min_price,
            the_product=the_product,
        )
        return the_product_to_be_saved

    @staticmethod
    async def prepare_child_matched_products(the_product, child_matched_products):
        to_be_saved = []

        for matched_product in child_matched_products:
            to_be_saved.append(ChildMatchedProduct(
                nm_id=matched_product['card'].get('nm_id'),
                title=matched_product['card'].get('imt_name'),
                vendor_name=matched_product['seller'].get('supplierName'),
                price=int(matched_product['detail']['salePriceU'] / 100),
                parent_nm_id=the_product.nm_id,
                vendor_code=matched_product['card'].get('vendor_code'),
                product=matched_product,
                is_correct=True,
                parent_id=the_product.id,
            ))
        return to_be_saved


def make_head(article: int):
    head = 'https://basket-{i}.wb.ru'

    if article < 14400000:
        number = '01'
    elif article < 28800000:
        number = '02'
    elif article < 43500000:
        number = '03'
    elif article < 72000000:
        number = '04'
    elif article < 100800000:
        number = '05'
    elif article < 106300000:
        number = '06'
    elif article < 111600000:
        number = '07'
    elif article < 117000000:
        number = '08'
    elif article < 131400000:
        number = '09'
    else:
        number = '10'
    return head.format(i=number)


def make_tail(article: str, item: str):
    length = len(str(article))
    if length <= 3:
        return f'/vol{0}/part{0}/{article}/info/' + item
    elif length == 4:
        return f'/vol{0}/part{article[0]}/{article}/info/' + item
    elif length == 5:
        return f'/vol{0}/part{article[:2]}/{article}/info/' + item
    elif length == 6:
        return f'/vol{article[0]}/part{article[:3]}/{article}/info/' + item
    elif length == 7:
        return f'/vol{article[:2]}/part{article[:4]}/{article}/info/' + item
    elif length == 8:
        return f'/vol{article[:3]}/part{article[:5]}/{article}/info/' + item
    else:
        return f'/vol{article[:4]}/part{article[:6]}/{article}/info/' + item
