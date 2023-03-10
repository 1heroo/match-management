import asyncio
import json
from match_management.utils import make_head, make_tail
import aiohttp
from comparison_management.whs import whs as wh_dicts


class CMUtils:

    @staticmethod
    async def make_get_request(url, headers):
        async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
            response = await session.get(url=url)
            if response.status == 200:
                return json.loads(await response.text())

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

        qnt_url = f'https://product-order-qnt.wildberries.ru/by-nm/?nm={article}'
        qnt = await self.make_get_request(url=qnt_url, headers={})

        obj.update({
            'card': card if card else {},
            'detail': detail[0] if detail else {},
            'seller': seller_data if seller_data else {},
            'qnt':  qnt if qnt else {}
        })
        return obj

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

        output_data += await asyncio.gather(*tasks)
        output_data = [item for item in output_data if not isinstance(item, Exception) and item]
        return output_data

    @staticmethod
    async def prepare_chars_for_output(products):
        output_data = []

        for product in products:
            article = product['card'].get('nm_id')

            salePriceU = product['detail'].get('salePriceU')
            priceU = product['detail'].get('priceU')

            if salePriceU:
                salePriceU //= 100
            if priceU:
                priceU //= 100

            qnt = product['qnt']
            if qnt:
                qnt = qnt[0].get('qnt')

            sale_sum = None
            if qnt and salePriceU:
                sale_sum = qnt * salePriceU

            obj = {
                'article wb': article,
                'supplier_id': product['detail'].get('supplierId'),
                '???????????????????????? ????????????????????': product['seller'].get('supplierName'),
                '????????????????????????': product['card'].get('name'),
                '??????????????????(subj_root_name)': product['card'].get('subj_root_name'),
                '????????????????????????(subj_name)': product['card'].get('subj_name', None),
                # '?????? ??????????????????(imt_name)': card.get('imt_name', None),
                '???????????? ?????? (vendor_code)': product['card'].get('vendor_code', None),
                '??????????': product['detail'].get('brand'),
                'id ????????????': product['detail'].get('brandId'),
                # '???????? (color)': card.get('nm_colors_names', None),
                # 'sale': data.get('sale', None),
                '????????': priceU,
                '???????? ???? ??????????????': salePriceU,
                'K??????????': qnt,
                '?????????????????? ?????????? ????????????': sale_sum,
                # '???????????? ??????????????': date_from,

                '????????(pics)': product['detail'].get('pics'),
                '????????????????': product['card'].get('description'),
                'feedbacks': product['detail'].get('feedbacks'),
                'rating': product['detail'].get('rating'),
                'compositions': [item.get('name') for item in product['card'].get('compositions', [])],
                '????????????': f'https://www.wildberries.ru/catalog/{article}/detail.aspx?targetUrl=BP'
            }

            options = product['card'].get('options', [])

            for option in options:
                name = option['name']

                obj.update({name: option['value']})

            sizes = product['detail'].get('sizes')

            wh_dict = {}
            for size in sizes:
                stocks = size.get('stocks')
                for stock in stocks:
                    wh = stock.get('wh')
                    wh_name = wh_dicts.get(int(wh))
                    qty = stock.get('qty')

                    if wh_dict.get(wh_name, None):
                        wh_dict[wh_name] += qty
                    else:
                        wh_dict[wh_name] = qty

            obj.update({
                'FBO': sum([value for key, value in wh_dict.items() if '????????????????' not in key]),
                'FBS': sum([value for key, value in wh_dict.items() if '????????????????' in key])
            })
            obj.update(wh_dict)
            output_data.append(obj)
        return output_data
