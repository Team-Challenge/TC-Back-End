from models.models import User, Shop


def create_test_user(session):
    user = User(full_name='John Doe', email='john@example.com')
    session.add(user)
    session.commit()
    return user


def test_create_user(session):
    # Example test for creating a user
    test_user = User(full_name='John Doe', email='john@example.com')
    session.add(test_user)
    session.commit()

    user = session.query(User).filter_by(id=test_user.id).first()

    assert user.id is not None
    assert user.full_name == 'John Doe'
    assert user.email == 'john@example.com'



def test_create_shop(session):
    # Example test for creating a user
    test_user = create_test_user(session)

    s = Shop(
        owner_id=test_user.id,
        name="Best Shop",
        description="Description",
        photo_shop="/images/test_path.png",
        banner_shop=1,
        phone_number="+399",
    )
    session.add(s)
    session.commit()

    shop = session.query(Shop).filter_by(id=s.id).first()

    assert shop.id is not None
    assert shop.owner_id == test_user.id
    assert shop.name == 'Best Shop'
    assert shop.description == 'Description'
    assert shop.photo_shop == '/images/test_path.png'
    assert int(shop.banner_shop) == 1
    assert shop.phone_number == '+399'