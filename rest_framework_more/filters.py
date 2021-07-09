from django.forms import ModelForm
from django_filters.rest_framework import FilterSet


def create_model_filter_form(
    model,
    debug=False,
    form_field_class_names=(
        "BooleanField",
        "CharField",
        "DateField",
        "DateTimeField",
        "DecimalField",
        "TextField",
    ),
):

    model_name = model.__name__
    if debug:
        print("model_name:", model_name)

    visible_fields = model._meta.get_fields(include_hidden=False)
    if debug:
        print("visible_fields:", visible_fields)

    form_field_names = [
        f.name
        for f in visible_fields
        if f.editable and f.__class__.__name__ in form_field_class_names
    ]
    if debug:
        print("form_field_names:", form_field_names)

    form_name = model_name + "Form"
    if debug:
        print("form_name:", form_name)

    form_defs = {"Meta": type("Meta", (), {"fields": form_field_names, "model": model})}

    form = type(form_name, (ModelForm,), form_defs)
    if debug:
        print("form:", form)

    return form


def create_model_filterset_class(
    model=None, form=None, debug=False, valid_lookups=None
):

    if form is None and model is None:
        raise Exception("you must pass in a form or model")

    if not form and model:
        form = create_model_filter_form(model)

    model = form.Meta.model
    if debug:
        print("model:", model)

    model_name = model.__name__
    if debug:
        print("model_name:", model_name)

    filter_name = model_name + "Filter"
    if debug:
        print("filter_name:", filter_name)

    visible_fields = model._meta.get_fields(include_hidden=False)
    if debug:
        print("visible_fields:", visible_fields)

    fields = {}
    for field in model._meta.get_fields(include_hidden=False):
        clazz = field.__class__

        # ManyToOneRel doesn't have get_lookups
        if hasattr(clazz, "get_lookups"):
            lookups = list(clazz.get_lookups().keys())

            # django-filter doesn't work with some field classes
            if clazz.__name__ in (
                "ImageField",
                "JSONField",
            ):
                continue

            # contains doesn't make sense for some fields
            if clazz.__name__ in (
                "AutoField",
                "BooleanField",
                "DateField",
                "DateTimeField",
                "DecimalField",
                "IntegerField",
                "NullBooleanField",
            ):
                lookups = [
                    lookup
                    for lookup in lookups
                    if lookup not in ("contains", "icontains")
                ]

            if debug:
                print("lookups:", lookups)
            if "date" in lookups:
                for extra_lookup in [
                    "date__gt",
                    "date__gte",
                    "date__lt",
                    "date__lte",
                    "date__range",
                ]:
                    if extra_lookup not in lookups:
                        lookups.append(extra_lookup)

            if valid_lookups:
                lookups = [lookup for lookup in lookups if lookup in valid_lookups]

            if debug:
                print("filtered lookups:", lookups)

            if lookups:
                fields[field.name] = lookups

    if debug:
        print("fields:", fields)

    filter_defs = {
        "Meta": type("Meta", (), {"fields": fields, "model": model, "form": form})
    }
    if debug:
        print("filter_defs:", filter_defs)

    filterset_class = type(filter_name, (FilterSet,), filter_defs)
    if debug:
        print("filterset_class:", filterset_class)

    return filterset_class
