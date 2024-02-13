from sqlalchemy import Enum

SubCategoryEnum = Enum('Заколки', 'Обручі', 'Резинки',
                        'Хустинки', 'Сережки', 'Моносережки',
                        'Зґарди', 'Шелести', 'Ґердани',
                        'Силянки', 'Кризи', 'Чокери',
                        'Намиста', 'Дукачі', 'Кулони та підвіски',
                        'Браслети', 'Каблучки', 'Котильйони', 'Брошки',
                        'Сумки', name='sub_category_enum')

SubCategoryDict = {
    'Заколки': 1,
    'Обручі': 2,
    'Резинки': 3,
    'Хустинки': 4,
    'Сережки': 5,
    'Моносережки': 6,
    'Зґарди': 7,
    'Шелести': 8,
    'Ґердани': 9,
    'Силянки': 10,
    'Кризи': 11,
    'Чокери': 12,
    'Намиста': 13,
    'Дукачі': 14,
    'Кулони та підвіски': 15,
    'Браслети': 16,
    'Каблучки': 17,
    'Котильйони': 18,
    'Брошки': 19,
    'Сумки': 20,
}


ProductStatus = Enum('В наявності', 'Під замовлення',
                    'В єдиному екземплярі', 'Немає в наявності', 
                    name='product_status')

Delivery_Post = Enum('nova_post', 'ukr_post', name='delivery_post')
