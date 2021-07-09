from rest_framework.serializers import ModelSerializer

from .mixins import FieldsMixin


def create_model_serializer_class(
    model, name=None, depth=10, fields="__all__", debug=False
):
    model_name = model.__name__
    if debug:
        print("model_name: " + model_name)

    serializer_name = name or model_name + "Serializer"
    if debug:
        print("serializer_name:", serializer_name)

    defs = {
        "Meta": type("Meta", (), {"depth": depth, "model": model, "fields": fields}),
        "__module__": __name__,
    }

    result = type(
        serializer_name,
        (
            FieldsMixin,
            ModelSerializer,
        ),
        defs,
    )

    if debug:
        print("result:", result)

    return result
