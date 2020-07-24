from django.forms import ModelForm
from django_filters.rest_framework import FilterSet


def create_model_filter_form(model, debug=False):

    model_name = model.__name__
    if debug:
        print("model_name:", model_name)

    filterable_fields = model._meta.get_fields(include_hidden=False)
    if debug:
        print("filterable_fields:", filterable_fields)

    filterable_field_names = [
        f.name
        for f in filterable_fields
        if f.__class__.__name__ in ("BooleanField", "CharField", "TextField")
    ]
    if debug:
        print("filterable_field_names:", filterable_field_names)

    form_name = model_name + "Form"
    if debug:
        print("form_name:", form_name)

    form_defs = {
        "Meta": type("Meta", (), {"fields": filterable_field_names, "model": model})
    }

    form = type(form_name, (ModelForm,), form_defs)
    if debug:
        print("form:", form)

    return form


def create_model_filterset_class(model=None, form=None, debug=False):

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

    fields = form.Meta.fields
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
