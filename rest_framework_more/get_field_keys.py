def get_field_keys(fields, path=""):
    previous = path + "." if path else ""
    results = []

    if hasattr(fields, "_meta"):
        fields = dict([(field.name, field) for field in fields._meta.get_fields()])

    for field_name, field in fields.items():
        if (
            field.__class__.__name__ == "NestedSerializer"
            or field.__class__.__name__ == "OrderedDict"
        ):
            subobj = field.fields if hasattr(field, "fields") else field
            for result in get_field_keys(subobj, previous + field_name):
                results.append(result)
        else:
            results.append(previous + field_name)
    return results
