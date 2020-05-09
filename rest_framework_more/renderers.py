from rest_framework_csv.renderers import CSVRenderer

class NonPaginatedCSVRenderer(CSVRenderer):
    format = 'csv (non-paginated)'

    def render(self, data, *args, **kwargs):
        info = args[1]

        view = info["view"]
        request = info["request"]

        queryset = view.queryset
        query_params = request.query_params.dict()
        query_params.pop('format', None)

        # filter out keys with empty strings
        filters = {k: v for k, v in query_params.items() if v != ''}

        queryset = queryset.filter(**filters)

        serializer = view.serializer_class

        data = serializer(queryset, many=True).data

        return super(NonPaginatedCSVRenderer, self).render(data, *args, **kwargs)

