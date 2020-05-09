# django-rest-framework-more
More Cool Django Rest Framework Stuff

# install
`pip3 install djangorestframework-more` or `pipenv install djangorestframework-more`

# features
#### NonPaginatedCSVRenderer
In case you want a CSV renderer that doesn't respect pagination:
```python
# in settings.py
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_more.renderers.NonPaginatedCSVRenderer
    ]
}
```
If you'd like to learn more about using renderers in Django Rest Framework, see https://www.django-rest-framework.org/api-guide/renderers/#setting-the-renderers

# contact
If you have any issues, feel free to post an issue at https://github.com/DanielJDufour/django-rest-framework-more/issues or email the package author at daniel.j.dufour@gmail.com
