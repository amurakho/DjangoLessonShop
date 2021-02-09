from uuslug import slugify
from transliterate import translit
from transliterate import exceptions
import random


def my_slugify(content):
    try:
        content = translit(content, reversed=True)
    except exceptions.LanguageDetectionError:
        pass

    slug = slugify(content)
    return f'{slug}-{random.randint(0, 10000)}'

