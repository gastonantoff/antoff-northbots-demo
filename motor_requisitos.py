def crear_requisito(
    codigo,
    nombre,
    tipo="texto",
    obligatorio=True,
    prioridad=0
):

    return {
        "codigo": codigo,
        "nombre": nombre,
        "tipo": tipo,
        "obligatorio": obligatorio,
        "prioridad": prioridad
    }


def evaluar_requisitos(
    requisitos,
    contexto
):

    datos_disponibles = contexto.get(
        "datos",
        {}
    )

    disponibles = []
    faltantes = []

    for requisito in requisitos:

        codigo = requisito["codigo"]

        valor = datos_disponibles.get(
            codigo
        )

        tiene_valor = (
            valor is not None
            and str(valor).strip() != ""
        )

        if tiene_valor:

            disponibles.append({
                "codigo": codigo,
                "nombre": requisito["nombre"],
                "valor": valor,
                "obligatorio": requisito["obligatorio"],
                "prioridad": requisito["prioridad"]
            })

        else:

            faltantes.append({
                "codigo": codigo,
                "nombre": requisito["nombre"],
                "tipo": requisito["tipo"],
                "obligatorio": requisito["obligatorio"],
                "prioridad": requisito["prioridad"]
            })

    faltantes_obligatorios = [
        requisito
        for requisito in faltantes
        if requisito["obligatorio"]
    ]

    return {
        "disponibles": disponibles,
        "faltantes": faltantes,
        "faltantes_obligatorios": (
            faltantes_obligatorios
        ),
        "listo_para_resolver": (
            len(faltantes_obligatorios) == 0
        )
    }


def obtener_siguiente_requisito(
    evaluacion
):

    faltantes = (
        evaluacion["faltantes_obligatorios"]
    )

    if not faltantes:

        return None

    faltantes_ordenados = sorted(
        faltantes,
        key=lambda requisito: (
            requisito["prioridad"]
        ),
        reverse=True
    )

    return faltantes_ordenados[0]


def analizar_resolucion(
    intencion,
    contexto,
    requisitos
):

    if not intencion:
        return {
            "estado": "INTENCION_NO_DETECTADA",
            "intencion": None,
            "evaluacion": None,
            "siguiente_requisito": None
        }

    evaluacion = evaluar_requisitos(
        requisitos=requisitos,
        contexto=contexto
    )

    siguiente_requisito = (
        obtener_siguiente_requisito(
            evaluacion
        )
    )

    if evaluacion["listo_para_resolver"]:

        estado = "LISTO_PARA_RESOLVER"

    else:

        estado = "INFORMACION_INCOMPLETA"

    return {
        "estado": estado,

        "intencion": intencion,

        "evaluacion": evaluacion,

        "siguiente_requisito": (
            siguiente_requisito
        )
    }