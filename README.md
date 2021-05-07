:warning: **Warning** NonPaginatedXLSXRenderer does not work with newer versions of [drf-renderer-xlsx](https://pypi.org/project/drf-renderer-xlsx/).  Please set your version of drf-renderer-xlsx to 0.3.8.

# django-rest-framework-more
More Cool Django Rest Framework Stuff

# install
`pip3 install djangorestframework-more` or `pipenv install djangorestframework-more`

# features
#### NonPaginatedCSVRenderer and NonPaginatedXLSXRenderer
In case you want a CSV or XLSX (Excel) renderer that doesn't respect pagination:
```python
# in settings.py
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_more.renderers.NonPaginatedCSVRenderer',
        'rest_framework_more.renderers.NonPaginatedXLSXRenderer'
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

#### FileNameMixin
The FileNameMixin automatically generates a more descriptive filename for CSV and Excel exports than the default "download".
It first tries to convert the url path into a filename.  If that doesn't succeed it tries to pull the filename from the queryset's model.
```python
# views.py
from rest_framework_more.mixins import FileNameMixin

class CarViewSet(FileNameMixin, ReadOnlyModelViewSet):
...    

# if the CarViewSet is called from the url /api/cars it will generate a download filename of api_cars.csv
```

# contact
If you have any issues, feel free to post an issue at https://github.com/DanielJDufour/django-rest-framework-more/issues or email the package author at daniel.j.dufour@gmail.com
