from sqlalchemy import Enum

SubCategoryEnum = Enum('заколки', 'обручі', 'резинки',
                        'хустинки', 'сережки', 'моносережки',
                        'згарди', 'шелести', 'гердани',
                        'силянки', 'кризи', 'чокери',
                        'намиста', 'дукачі', 'кулони та підвіски',
                        'браслети', 'каблучки', 'котильйони', 'брошки',
                        'сумки', name='sub_category_enum')

ProductStatus = Enum('В наявності', 'Під замовлення',
                    'В єдиному екземплярі', 'Немає в наявності', 
                    name='product_status')

Delivery_Post = Enum('nova_post', 'ukr_post', name='delivery_post')
