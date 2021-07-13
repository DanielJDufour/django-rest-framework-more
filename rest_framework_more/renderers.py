from collections import OrderedDict

import simple_env as se
from drf_renderer_xlsx.renderers import XLSXRenderer
from rest_framework_csv.renderers import CSVRenderer

from .get_field_keys import get_field_keys

DEBUG = se.get("DEBUG_DRF_MORE") or False

PREFETCH_MAX = se.get("DRF_PREFETCH_MAX") or 100

try:
    from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
except Exception:
    ILLEGAL_CHARACTERS_RE = None


class NonPaginatedCSVRenderer(CSVRenderer):
    format = "csv (non-paginated)"

    def render(self, data, accepted_media_type, renderer_context):
        response = renderer_context["response"]

        if response.status_code != 200:
            return ""

        view = renderer_context["view"]
        request = renderer_context["request"]

        queryset = view.queryset or view.get_queryset()
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

        return super().render(data, accepted_media_type, renderer_context)


def get(data, path):
    try:
        original_data = data
        for part in path.split("."):
            if data is None or part not in data:
                return None
            data = data[part]
            if data is None:
                return None
        return data
    except Exception as e:
        print("original_data:", original_data)
        print("path:", path)
        raise e


def has_consecutive_repeat(data):
    for i in range(1, len(data)):
        if data[i - 1] == data[i]:
            return True
    return False


# cleans a path, so it resolves to a model and not a field
def get_model_path(model, path):
    model_path = []

    for field_name in path:
        field = model._meta.get_field(field_name)
        if field.__class__.__name__ == "ForeignKey":
            model_path.append(field_name)
            model = field.related_model
        else:
            break

    return model_path


def get_model_by_path(model, path):
    if isinstance(path, str):
        if "." in path:
            path = path.split(".")
        elif "__" in path:
            path = path.split("__")
        else:
            path = [path]

    for field_name in path[:-1]:
        model = model._meta.get_field(field_name).related_model

    # check if last part of path is a foreign key or not
    last_field = model._meta.get_field(path[-1])
    if last_field.__class__.__name__ == "ForeignKey":
        model = last_field.related_model

    return model


class NonPaginatedXLSXRenderer(XLSXRenderer):
    format = "xlsx (non-paginated)"

    def render(self, data, accepted_media_type, renderer_context):
        response = renderer_context["response"]

        if response.status_code != 200:
            return ""

        view = renderer_context["view"]
        request = renderer_context["request"]

        queryset = view.queryset or view.get_queryset()
        query_params = request.query_params.dict()
        query_params.pop("format", None)

        # ignore the page parameter
        query_params.pop("page", None)

        # ignore the fields parameter
        fields = query_params.pop("fields", None)

        # filter out keys with empty strings
        filters = {k: v for k, v in query_params.items() if v != ""}

        model = queryset[0].__class__

        model_fields = model._meta.get_fields(include_hidden=False)

        model.__name__

        # get paths to model fields and related fields
        # by traversing the model classes without db queries
        model_field_paths = get_field_keys(model)
        if DEBUG:
            print("[django-rest-framework-more] model_field_paths:", model_field_paths)

        fields_to_clean = [
            field.name
            for field in model_fields
            if "Boolean" in field.__class__.__name__
            or "Integer" in field.__class__.__name__
        ]
        if DEBUG:
            print("fields_to_clean:", fields_to_clean)

        # clean filter input
        filters = {
            k: (se.clean(v) if k in fields_to_clean else v) for k, v in filters.items()
        }

        if DEBUG:
            print("filters (after cleaning):", filters)

        related_paths = [
            path
            for path in (filters.keys() if filters else model_field_paths)
            if "." in path
        ]
        if DEBUG:
            print("[django-rest-framework-more] related_path_lookups:", related_paths)

        # convert paths to fields to paths to models
        related_model_paths = list(
            {
                "__".join(get_model_path(model, path.split(".")))
                for path in related_paths
            }
        )
        if DEBUG:
            print(
                "[django-rest-framework-more] related_model_paths:", related_model_paths
            )

        for path in related_model_paths:
            try:
                if (
                    get_model_by_path(model, path).objects.using(queryset.db).count()
                    <= PREFETCH_MAX
                ):
                    if DEBUG:
                        print("[django-rest-framework-more] prefetching:" + path)
                    queryset = queryset.prefetch_related(path)
            except Exception as e:
                print(e)

        queryset = queryset.filter(**filters)
        if DEBUG:
            print("queryset (after filtering):", queryset)

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
        if DEBUG:
            print("# keys after first pass", sorted(keys))

        # remove any null foreign keys
        keys = [
            key
            for key in keys
            if not any([other_key.startswith(key + ".") for other_key in keys])
        ]
        if DEBUG:
            print("# keys after removing null foreign keys", keys)

        # filter out recursive lookups
        keys = [key for key in keys if not has_consecutive_repeat(key.split("."))]
        if DEBUG:
            print("# keys after filtering likely recursive lookups", keys)

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
                elif isinstance(value, str):
                    value = ILLEGAL_CHARACTERS_RE.sub("", value)
                flat_row.append((key, value))
            flat_data.append(OrderedDict(flat_row))

        if DEBUG:
            print("post-flattening flat_data[0]", flat_data[0])
            if len(flat_data) > 1:
                print("post-flattening flat_data[1]", flat_data[1])
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

        return super().render(flat_data, accepted_media_type, renderer_context)
