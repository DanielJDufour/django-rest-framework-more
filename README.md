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
        'rest_framework_more.renderers.NonPaginatedCSVRenderer'
    ]
}
```
If you'd like to learn more about using renderers in Django Rest Framework, see https://www.django-rest-framework.org/api-guide/renderers/#setting-the-renderers

#### Creater Model Serializer Class
```python
# in serializers.py
from app.models import Car
from rest_framework_more.serializers import create_model_serializer_class

CarSerializer = create_model_serializer_class(model=Car)
```

#### Create Model Filter Form
```python
# forms.py
from app.models import Car
from rest_framework_more.filters import create_model_filter_form

CarFilterForm = create_model_filter_form(model=Car)
```

#### Create Model Filter Set Class
```python
# forms.py
from app.models import Car
from rest_framework_more.filters import create_model_filterset_class

CarFilterSet = create_model_filterset_class(model=Car)
```

#### Create Model ViewSet Class
```python
# views.py
from app.models import Car
from rest_framework_more.viewsets import create_model_viewset_class

CarViewSet = create_model_viewset_class(model=Car)
```

# contact
If you have any issues, feel free to post an issue at https://github.com/DanielJDufour/django-rest-framework-more/issues or email the package author at daniel.j.dufour@gmail.com
