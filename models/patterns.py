from sqlalchemy import Enum
from typing import Union

SubCategoryEnumDict = {
    11: 'Заколки',
    12: 'Обручі',
    13: 'Резинки',
    14: 'Хустинки',
    21: 'Сережки',
    22: 'Моносережки',
    31: 'Зґарди',
    32: 'Шелести',
    33: 'Ґердани',
    34: 'Силянки',
    35: 'Кризи',
    36: 'Чокери',
    37: 'Намиста',
    38: 'Дукачі',
    39: 'Кулони та підвіски',
    41: 'Браслети',
    42: 'Каблучки',
    51: 'Котильйони',
    52: 'Брошки',
    53: 'Сумки',
    61: 'Набір'
}

SubCategoryDict = {value: key for key, value in SubCategoryEnumDict.items()}
SubCategoryEnum = Enum(*list(SubCategoryEnumDict.items()), name='sub_category_enum')


def get_subcategory(val: Union[str, int]) -> Union[int, str]:
    if isinstance(val, str):
        return SubCategoryDict[val]
    if isinstance(val, int):
        return SubCategoryEnumDict[val]
    raise TypeError("Wrong subcategory type. Should be str or int.")


ProductStatus = Enum('В наявності', 'Під замовлення',
                    'В єдиному екземплярі', 'Немає в наявності', 
                    name='product_status')

Delivery_Post = Enum('nova_post', 'ukr_post', name='delivery_post')
