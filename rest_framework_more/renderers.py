from collections import OrderedDict
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


def get(data, path):
    for part in path.split("."):
        if data:
            data = data[part]
            if data is None:
                return None
    return data


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

        keys = []
        for row in data:
            previous = None
            for key in get_field_keys(row):
                if key not in keys:
                    if previous:
                        index = keys.index(previous) + 1
                        keys = keys[:index] + [key] + keys[index:]
                    else:
                        keys.append(key)
                previous = key

        # remove any null foreign keys
        keys = [
            key
            for key in keys
            if not any([other_key.startswith(key + ".") for other_key in keys])
        ]

        # reformat the input data
        flat_data = []
        for row in data:
            flat_data.append(OrderedDict([(key, get(row, key)) for key in keys]))

        if fields:
            fields = fields.split(",")

            # sort column titles to match how
            # XLSXRenderer will return the data
            column_titles = sorted(fields, key=lambda field: keys.index(field))
        else:
            column_titles = keys

        if hasattr(view, "column_header"):
            if "titles" not in view.column_header:
                view.column_header["titles"] = column_titles
        else:
            view.column_header = {"titles": column_titles}

        return super(NonPaginatedXLSXRenderer, self).render(
            flat_data, accepted_media_type, renderer_context
        )
