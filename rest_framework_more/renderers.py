from rest_framework_csv.renderers import CSVRenderer
from drf_renderer_xlsx.renderers import XLSXRenderer
from .get_field_keys import get_field_keys


class NonPaginatedCSVRenderer(CSVRenderer):
    format = "csv (non-paginated)"

    def render(self, data, accepted_media_type, renderer_context):
        response = renderer_context["response"]

        if response.status_code != 200:
            return ""

        view = renderer_context["view"]
        request = renderer_context["request"]

        queryset = view.queryset
        query_params = request.query_params.dict()
        query_params.pop("format", None)

        # ignore the page parameter
        query_params.pop("page", None)

        # ignore the fields parameter
        query_params.pop("fields", None)

        # filter out keys with empty strings
        filters = {k: v for k, v in query_params.items() if v != ""}

        queryset = queryset.filter(**filters)

        serializer = view.serializer_class

        data = serializer(queryset, context={"request": request}, many=True).data

        return super(NonPaginatedCSVRenderer, self).render(
            data, accepted_media_type, renderer_context
        )


class NonPaginatedXLSXRenderer(XLSXRenderer):
    format = "xlsx (non-paginated)"

    def render(self, data, accepted_media_type, renderer_context):
        response = renderer_context["response"]

        if response.status_code != 200:
            return ""

        view = renderer_context["view"]
        request = renderer_context["request"]

        queryset = view.queryset
        query_params = request.query_params.dict()
        query_params.pop("format", None)

        # ignore the page parameter
        query_params.pop("page", None)

        # ignore the fields parameter
        fields = query_params.pop("fields", None)

        # filter out keys with empty strings
        filters = {k: v for k, v in query_params.items() if v != ""}

        queryset = queryset.filter(**filters)

        serializer = view.serializer_class

        data = serializer(queryset, context={"request": request}, many=True).data

        if fields:
            fields = fields.split(",")

            keys = get_field_keys(data[0], path="")

            # sort column titles to match how
            # XLSXRenderer will return the data
            column_titles = sorted(fields, key=lambda field: keys.index(field))

            if hasattr(view, "column_header"):
                if "titles" not in view.column_header:
                    view.column_header["titles"] = column_titles
            else:
                view.column_header = {"titles": column_titles}

        return super(NonPaginatedXLSXRenderer, self).render(
            data, accepted_media_type, renderer_context
        )
