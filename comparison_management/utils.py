

class CMUtils:

    @staticmethod
    async def prepare_chars_for_output(products):
        output_data = []

        for product in products:

            salePriceU = product['detail'].get('salePriceU')
            priceU = product['detail'].get('priceU')

            if salePriceU:
                salePriceU //= 100
            if priceU:
                product //= 100

            obj = {
                'article wb': product['card'].get('nm_id'),
                'supplier_id': product['detail'].get('supplierId'),
                'Наименование Поставщика': product['seller'].get('supplierName'),
                'Наименование': product['card'].get('name'),
                'Категория(subj_root_name)': product['card'].get('subj_root_name'),
                'Подкатегория(subj_name)': product['card'].get('subj_name', None),
                # 'Вид Категории(imt_name)': card.get('imt_name', None),
                'Вендор Код (vendor_code)': product['card'].get('vendor_code', None),
                # 'Цвет (color)': card.get('nm_colors_names', None),
                # 'sale': data.get('sale', None),


                # 'Цена': priceU,
                # 'Цена со скидкой': salePriceU,
                # 'Kупили': qnt,
                # 'Сумма продаж': int(int(data["salePriceU"] / 100) * qnt),
                # 'Начало продажи': date_from,
                # 'Бренд': data.get('brand', None),
                # 'id бренда': int(data.get('brandId', False)),
                # 'season': card.get('season', None),
                # 'Фото(pics)': int(data.get('pics', False)),
                # 'Пол(kinds)': card.get('kinds', None),
                # 'feedbacks': data.get('feedbacks', None),
                # 'rating': data.get('rating', None),
                # 'compositions': [item.get('name') for item in compositions] if compositions is not None else None,
                # 'Ссылка': f'https://www.wildberries.ru/catalog/{article}/detail.aspx?targetUrl=BP'
            }

        return output_data
