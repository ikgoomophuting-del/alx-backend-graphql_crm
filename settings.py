pip install django-filter

INSTALLED_APPS = [
    ...,
    'graphene_django',
    'django_filters',
    'crm',
]

GRAPHENE = {
    'SCHEMA': 'graphql_crm.schema.schema',
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware',
    ]
}
