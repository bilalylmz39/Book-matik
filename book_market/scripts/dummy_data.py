import os
import random
import requests
import django
from django.contrib.auth.models import User
from faker import Faker
from books.api.serializers import BookSerializer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_market.settings')

django.setup()


def set_user():
    fake = Faker("en_US")

    f_name = fake.first_name()
    l_name = fake.last_name()
    u_name = f'{f_name.lower()}_{l_name.lower()}'
    email = f'{u_name}@{fake.domain_name()}'
    print(f_name, l_name, email)

    user_check = User.objects.filter(username=u_name)
    while user_check.exists():
        u_name = u_name + str(random.randrange(1, 99))
        user_check = User.objects.filter(username=u_name)

    user = User(
        first_name=f_name,
        last_name=l_name,
        username=u_name,
        email=email
    )

    user.set_password('testing...')
    user.save()


def get_books(topic):
    url = 'https://openlibrary.org/search.json'
    payload = {'q': topic}
    response = requests.get(url, params=payload)

    if response.status_code != 200:
        print('Bad request:', response.status_code)
        return

    data = response.json()
    books = data.get('docs', [])

    for book in books[:50]:
        book_name = book.get('title', '')
        text = book.get('text', [])
        if not isinstance(text, list):
            text = [str(text)]

        data = dict(
            name=book.get('title', 'Unknown'),
            author=book.get('author_name', ['Unknown'])[0],
            description='This is a dummy description.',
            published_date='2023-01-01'
        )

        serializer = BookSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print('Book created:', book_name)
        else:
            print(serializer.errors)
