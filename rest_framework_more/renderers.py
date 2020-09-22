from collections import Counter
from collections import OrderedDict
from rest_framework_csv.renderers import CSVRenderer
from drf_renderer_xlsx.renderers import XLSXRenderer
from .get_field_keys import get_field_keys

DEBUG = False


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
    try:
        original_data = data
        for part in path.split("."):
            if data:
                data = data[part]
                if data is None:
                    return None
        return data
    except Exception as e:
        print("original_data:", original_data)
        print("path:", path)
        raise e


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
        if DEBUG:
            print("pre-cleaning len(data)", len(data))

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

        if DEBUG:
            print("keys:", keys)
            print("len(keys):", len(keys))

        # reformat the input data
        flat_data = []
        for row in data:
            flat_row = []
            for key in keys:
                value = get(row, key)
                # don't want empty dicts because that throws off XLSXRenderer
                if isinstance(value, dict) and len(value) == 0:
                    value = None
                flat_row.append((key, value))
            flat_data.append(OrderedDict(flat_row))

        if DEBUG:
            print("post-flattening flat_data[0]", flat_data[0])
            print("post-flattening len(flat_data)", len(flat_data))

        if fields:
            fields = fields.split(",")

            # sort column titles to match how
            # XLSXRenderer will return the data
            column_titles = sorted(fields, key=lambda field: keys.index(field))
        else:
            column_titles = keys

        if DEBUG:
            print("column_titles:", column_titles)

        if hasattr(view, "column_header"):
            if "titles" not in view.column_header:
                view.column_header["titles"] = column_titles
        else:
            view.column_header = {"titles": column_titles}

        return super(NonPaginatedXLSXRenderer, self).render(
            flat_data, accepted_media_type, renderer_context
        )
