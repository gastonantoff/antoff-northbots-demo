from db_manager import (
    obtener_acciones_herramienta,
    obtener_accion_herramienta
)


def crear_herramienta(
    codigo,
    nombre,
    descripcion="",
    operacion="",
    parametros=None,
    permiso_requerido=None,
    requiere_confirmacion=False,
    permite_ejecucion_autonoma=True,
    prioridad=0
):

    if parametros is None:
        parametros = []

    return {
        "codigo": codigo,
        "nombre": nombre,
        "descripcion": descripcion,
        "operacion": operacion,
        "parametros": parametros,
        "permiso_requerido": permiso_requerido,
        "requiere_confirmacion": requiere_confirmacion,
        "permite_ejecucion_autonoma": permite_ejecucion_autonoma,
        "prioridad": prioridad,
        "activo": True
    }


def herramienta_activa(herramienta):

    return herramienta.get(
        "activo",
        False
    )


def puede_ejecutar_autonomamente(
    herramienta
):

    return (
        herramienta.get(
            "activo",
            False
        )
        and
        herramienta.get(
            "permite_ejecucion_autonoma",
            False
        )
        and
        not herramienta.get(
            "requiere_confirmacion",
            False
        )
    )


def obtener_parametros_herramienta(
    herramienta
):

    parametros = herramienta.get(
        "parametros",
        []
    )

    if isinstance(parametros, str):
        return []

    return parametros


def validar_parametros_herramienta(
    herramienta,
    datos
):

    parametros = (
        obtener_parametros_herramienta(
            herramienta
        )
    )

    faltantes = []

    for parametro in parametros:

        codigo = parametro.get(
            "codigo"
        )

        obligatorio = parametro.get(
            "obligatorio",
            True
        )

        if not obligatorio:
            continue

        valor = datos.get(
            codigo
        )

        if (
            valor is None
            or str(valor).strip() == ""
        ):

            faltantes.append(
                parametro
            )

    return {
        "valido": len(faltantes) == 0,
        "faltantes": faltantes
    }


def preparar_ejecucion(
    herramienta,
    datos
):

    if not herramienta:

        return {
            "estado": "HERRAMIENTA_NO_ENCONTRADA",
            "herramienta": None,
            "datos": datos,
            "faltantes": []
        }

    if not herramienta_activa(
        herramienta
    ):

        return {
            "estado": "HERRAMIENTA_INACTIVA",
            "herramienta": herramienta,
            "datos": datos,
            "faltantes": []
        }

    validacion = (
        validar_parametros_herramienta(
            herramienta,
            datos
        )
    )

    if not validacion["valido"]:

        return {
            "estado": "PARAMETROS_INCOMPLETOS",
            "herramienta": herramienta,
            "datos": datos,
            "faltantes": validacion[
                "faltantes"
            ]
        }

    if herramienta.get(
        "requiere_confirmacion",
        False
    ):

        return {
            "estado": "REQUIERE_CONFIRMACION",
            "herramienta": herramienta,
            "datos": datos,
            "faltantes": []
        }

    if not puede_ejecutar_autonomamente(
        herramienta
    ):

        return {
            "estado": "EJECUCION_NO_AUTONOMA",
            "herramienta": herramienta,
            "datos": datos,
            "faltantes": []
        }

    return {
        "estado": "LISTA_PARA_EJECUTAR",
        "herramienta": herramienta,
        "datos": datos,
        "faltantes": []
    }


def convertir_accion_a_herramienta(
    accion
):

    if not accion:
        return None

    return {
        "id": accion[0],
        "nombre": accion[1],
        "operacion": accion[2],
        "descripcion": accion[3],
        "parametros": accion[4],
        "activo": accion[5] == 1
    }


def obtener_herramientas(
    herramienta_id
):

    acciones = (
        obtener_acciones_herramienta(
            herramienta_id
        )
    )

    herramientas = []

    for accion in acciones:

        herramienta = (
            convertir_accion_a_herramienta(
                accion
            )
        )

        if herramienta:
            herramientas.append(
                herramienta
            )

    return herramientas


def obtener_herramienta(
    accion_id
):

    accion = (
        obtener_accion_herramienta(
            accion_id
        )
    )

    return convertir_accion_a_herramienta(
        accion
    )


def seleccionar_herramienta(
    herramientas,
    operacion
):

    candidatas = []

    for herramienta in herramientas:

        if not herramienta_activa(
            herramienta
        ):
            continue

        if herramienta.get(
            "operacion"
        ) != operacion:
            continue

        candidatas.append(
            herramienta
        )

    if not candidatas:

        return None

    candidatas.sort(
        key=lambda herramienta:
        herramienta.get(
            "prioridad",
            0
        ),
        reverse=True
    )

    return candidatas[0]


def ejecutar_herramienta(
    herramienta,
    datos
):

    preparacion = (
        preparar_ejecucion(
            herramienta,
            datos
        )
    )

    estado = preparacion[
        "estado"
    ]

    if estado != "LISTA_PARA_EJECUTAR":

        return {
            "estado": estado,
            "exito": False,
            "herramienta": herramienta,
            "datos": datos,
            "resultado": None,
            "error": None,
            "faltantes": preparacion[
                "faltantes"
            ]
        }

    return {
        "estado": "EJECUTADA",
        "exito": True,
        "herramienta": herramienta,
        "datos": datos,
        "resultado": {
            "operacion": herramienta.get(
                "operacion"
            ),
            "parametros": datos
        },
        "error": None,
        "faltantes": []
    }