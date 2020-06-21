from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework_csv.renderers import PaginatedCSVRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet


from .filters import create_filterset_class
from .renderers import NonPaginatedCSVRenderer
from .serializers import create_model_serializer_class

def create_viewset_class(model, serializer=None, filterset_class=None, queryset=None, debug=False, renderer_classes=(BrowsableAPIRenderer, JSONRenderer, PaginatedCSVRenderer, NonPaginatedCSVRenderer, )):
    if not model:
        raise Exception("You must pass in a model")

    model_name = model.__name__
    if debug: print("model_name:", model_name)

    if model and not filterset_class:
        filterset_class = create_filterset_class(model)

    if model and not serializer:
        serializer = create_model_serializer_class(model)

    if not queryset:
        queryset = model.objects.all()

    fields = model._meta.get_fields(include_hidden=True)
    if debug: print("fields:", fields)

    text_fields = [f.name for f in fields if f.__class__.__name__ in ("CharField", "TextField")]
    if debug: print("text_fields:", text_fields)

    viewset_name = model_name + "ViewSet"
    if debug: print("viewset_name:", viewset_name)

    defs = {
        "renderer_classes": renderer_classes,
        "queryset": queryset,
        "serializer_class": serializer,
        "filter_backends": [DjangoFilterBackend, SearchFilter, OrderingFilter],
        "filterset_class": filterset_class,
        "search_fields": text_fields,
        "ordering_fields": "__all__"
    }

    viewset = type(viewset_name, (ReadOnlyModelViewSet,), defs)
    if debug: print("viewset:", viewset)

    return viewset