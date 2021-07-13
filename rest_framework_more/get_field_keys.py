from collections import OrderedDict


def get_field_keys(fields, path=""):
    previous = path + "." if path else ""
    results = []

    if hasattr(fields, "_meta"):
        fields = OrderedDict(
            [
                (field.name, field)
                for field in fields._meta.get_fields()
                # don't want to go backwards
                if (field.__class__.__name__ != "ManyToOneRel") and
                # avoid recursive self references
                not (
                    field.__class__.__name__ == "ForeignKey"
                    and field.related_model == fields
                )
            ]
        )

    for field_name, field in fields.items():
        if field.__class__.__name__ in [
            "NestedSerializer",
            "OrderedDict",
            "dict",
            "ForeignKey",
        ]:
            subobj = None
            if hasattr(field, "fields"):
                subobj = field.fields
            elif hasattr(field, "related_model"):
                subobj = field.related_model
            else:
                subobj = field
            for result in get_field_keys(subobj, previous + field_name):
                results.append(result)
        else:
            results.append(previous + field_name)
    return results
