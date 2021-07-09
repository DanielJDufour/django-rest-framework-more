from django_filters.rest_framework import DjangoFilterBackend
from drf_renderer_xlsx.renderers import XLSXRenderer
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_csv.renderers import PaginatedCSVRenderer

from .filters import create_model_filterset_class
from .mixins import FileNameMixin
from .renderers import NonPaginatedCSVRenderer, NonPaginatedXLSXRenderer
from .serializers import create_model_serializer_class


def create_model_viewset_class(
    model,
    serializer=None,
    filter_backends=(DjangoFilterBackend, SearchFilter, OrderingFilter),
    filterset_class=None,
    get_queryset=None,
    queryset=None,
    debug=False,
    renderer_classes=(
        BrowsableAPIRenderer,
        JSONRenderer,
        PaginatedCSVRenderer,
        NonPaginatedCSVRenderer,
        XLSXRenderer,
        NonPaginatedXLSXRenderer,
    ),
    valid_lookups=None,
):
    if not model:
        raise Exception("You must pass in a model")

    model_name = model.__name__
    if debug:
        print("model_name:", model_name)

    if model and not filterset_class:
        filterset_class = create_model_filterset_class(
            model=model, valid_lookups=valid_lookups
        )

    if model and not serializer:
        serializer = create_model_serializer_class(model=model)

    if not get_queryset and not queryset:
        queryset = model.objects.all()

    fields = model._meta.get_fields(include_hidden=True)
    if debug:
        print("fields:", fields)

    text_fields = [
        f.name for f in fields if f.__class__.__name__ in ("CharField", "TextField")
    ]
    if debug:
        print("text_fields:", text_fields)

    viewset_name = model_name + "ViewSet"
    if debug:
        print("viewset_name:", viewset_name)

    defs = {
        "renderer_classes": renderer_classes,
        "serializer_class": serializer,
        "filter_backends": filter_backends,
        "filterset_class": filterset_class,
        "search_fields": text_fields,
        "ordering_fields": "__all__",
    }
    if get_queryset:
        defs["basename"] = model_name.lower()
        defs["get_queryset"] = get_queryset

    # we have to add "is not None" or the queryset is evaluated
    elif queryset is not None:
        defs["queryset"] = queryset

    viewset = type(
        viewset_name,
        (
            FileNameMixin,
            ReadOnlyModelViewSet,
        ),
        defs,
    )
    if debug:
        print("viewset:", viewset)

    return viewset
