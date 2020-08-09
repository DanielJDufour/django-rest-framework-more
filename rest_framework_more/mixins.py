from rest_framework.response import Response


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
