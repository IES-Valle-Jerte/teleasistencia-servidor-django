from django.db.models import Q


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