from django.db.models import Q

from rest_framework.response import Response

# En el caso de que queramos que la búsqueda pueda coincidir con TODOS de los valores
def getQueryAnd(params):
    query = None
    for key in params:
        val = params[key]
        if query is None:
            query = Q(**{key: val})
        else:
            query = query & Q(**{key: val})

    return query

# En el caso de que queramos que la búsqueda pueda coincidir con ALGUNO de los valores
def getQueryOr(params):
    query = None
    for key in params:
        val = params[key]
        if query is None:
            query = Q(**{key: val})
        else:
            query = query | Q(**{key: val})
    return query


# Ejemplo de cómo se haría un PATCH genérico para cualquier petición de API-REST de tipo PATHC
# para añadirlo simplemente hay que sobrescribir el método partial_update
# Se puede ver un ejejmplo en view_rest.py -> Paciente_ViewSet
def partial_update_generico(view, request, *args, **kwargs):
    instance = view.queryset.get(pk=kwargs["pk"])
    serializer = view.get_serializer(instance, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    view.perform_update(serializer)
    return serializer.data


def normalizar_booleano(value):
    """
    Normaliza un valor boolean o cadena de texto representando un boolean como un booleano
    """

    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() == 'true'
    else:
        return None  # or handle the invalid value in a way that makes sense for your application