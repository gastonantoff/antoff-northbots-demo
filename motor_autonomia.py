def crear_control_autonomia(
    max_pasos=10,
    max_errores=3,
    max_reintentos=2
):

    return {
        "max_pasos": max_pasos,
        "max_errores": max_errores,
        "max_reintentos": max_reintentos,
        "pasos_ejecutados": 0,
        "errores": 0,
        "reintentos": 0,
        "estado": "ACTIVO"
    }


def verificar_limites(
    control
):

    if control["pasos_ejecutados"] >= control["max_pasos"]:

        return {
            "permitido": False,
            "motivo": "LIMITE_DE_PASOS"
        }

    if control["errores"] >= control["max_errores"]:

        return {
            "permitido": False,
            "motivo": "LIMITE_DE_ERRORES"
        }

    if control["reintentos"] >= control["max_reintentos"]:

        return {
            "permitido": False,
            "motivo": "LIMITE_DE_REINTENTOS"
        }

    return {
        "permitido": True,
        "motivo": None
    }


def verificar_herramienta(
    herramienta
):

    if not herramienta:

        return {
            "permitido": False,
            "motivo": "HERRAMIENTA_NO_ENCONTRADA"
        }

    if not herramienta.get(
        "activo",
        False
    ):

        return {
            "permitido": False,
            "motivo": "HERRAMIENTA_INACTIVA"
        }

    if not herramienta.get(
        "permite_ejecucion_autonoma",
        False
    ):

        return {
            "permitido": False,
            "motivo": "AUTONOMIA_NO_PERMITIDA"
        }

    if herramienta.get(
        "requiere_confirmacion",
        False
    ):

        return {
            "permitido": False,
            "motivo": "REQUIERE_CONFIRMACION"
        }

    return {
        "permitido": True,
        "motivo": None
    }


def registrar_paso(
    control
):

    control["pasos_ejecutados"] += 1

    return control


def registrar_error(
    control
):

    control["errores"] += 1

    return control


def registrar_reintento(
    control
):

    control["reintentos"] += 1

    return control


def autorizar_ejecucion(
    control,
    herramienta
):

    if control.get(
        "estado"
    ) != "ACTIVO":

        return {
            "autorizado": False,
            "accion": "DETENER",
            "motivo": "CONTROL_INACTIVO"
        }

    limites = verificar_limites(
        control
    )

    if not limites["permitido"]:

        control["estado"] = "DETENIDO"

        return {
            "autorizado": False,
            "accion": "DETENER",
            "motivo": limites["motivo"]
        }

    herramienta_resultado = (
        verificar_herramienta(
            herramienta
        )
    )

    if not herramienta_resultado["permitido"]:

        motivo = herramienta_resultado[
            "motivo"
        ]

        if motivo == "REQUIERE_CONFIRMACION":

            return {
                "autorizado": False,
                "accion": "CONFIRMAR",
                "motivo": motivo
            }

        return {
            "autorizado": False,
            "accion": "DETENER",
            "motivo": motivo
        }

    registrar_paso(
        control
    )

    return {
        "autorizado": True,
        "accion": "EJECUTAR",
        "motivo": None
    }


def procesar_resultado(
    control,
    resultado
):

    if not resultado:

        registrar_error(
            control
        )

        return {
            "estado": "ERROR",
            "continuar": False
        }

    if resultado.get(
        "exito",
        False
    ):

        return {
            "estado": "EXITO",
            "continuar": True
        }

    registrar_error(
        control
    )

    limites = verificar_limites(
        control
    )

    if limites["permitido"]:

        return {
            "estado": "ERROR",
            "continuar": True
        }

    control["estado"] = "DETENIDO"

    return {
        "estado": "ERROR",
        "continuar": False
    }


def finalizar_control(
    control,
    motivo="FINALIZADO"
):

    control["estado"] = "FINALIZADO"

    return {
        "estado": "FINALIZADO",
        "motivo": motivo,
        "pasos_ejecutados": control[
            "pasos_ejecutados"
        ],
        "errores": control[
            "errores"
        ],
        "reintentos": control[
            "reintentos"
        ]
    }