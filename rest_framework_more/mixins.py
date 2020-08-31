from rest_framework.response import Response
from prune import prune
from .subpaths import subpaths


def get_field_keys(fields, path):
    previous = path + "." if path else ""
    results = []
    for field_name, field in fields.items():
        if field.__class__.__name__ == "NestedSerializer":
            for result in get_field_keys(field.fields, previous + field_name):
                results.append(result)
        else:
            results.append(previous + field_name)
    return results


class FileNameMixin(object):
    def get_filename(self, request, response):
        try:
            return request.path_info.replace("/", "_").strip("_")
        except:
            pass

        try:
            return self.queryset.model.__name__
        except:
            return "download"

    def finalize_response(self, request, response, *args, **kwargs):
        response = super(FileNameMixin, self).finalize_response(
            request, response, *args, **kwargs
        )
        if isinstance(response, Response):
            if "xlsx" in response.accepted_renderer.format:
                filename = self.get_filename(request, response) + ".xlsx"
            elif "csv" in response.accepted_renderer.format:
                filename = self.get_filename(request, response) + ".csv"
            else:
                filename = None

            if filename:
                response["content-disposition"] = f"attachment; filename={filename}"

        return response


class FieldsMixin(object):
    def to_representation(self, *args, **kwargs):
        ret = super(FieldsMixin, self).to_representation(*args, **kwargs)

        try:
            fields = self.context["request"].query_params.get("fields")
            if fields:
                fields_to_keep = fields.split(",")

                all_fields = get_field_keys(self.fields, "")

                remove_these_fields = []
                for field in all_fields:
                    for subpath in subpaths(field):
                        if subpath in remove_these_fields:
                            break

                        if not any([f.startswith(subpath) for f in fields_to_keep]):
                            remove_these_fields.append(subpath)
                            break

                prune(ret, remove_these_fields)
        except Exception as e:
            print(e)

        return ret
