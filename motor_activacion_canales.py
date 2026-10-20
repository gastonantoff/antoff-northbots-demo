ESTADO_ACTIVADO = "ACTIVADO"
ESTADO_BLOQUEADO = "BLOQUEADO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"


def validar_conexion(resultado):
    """
    Comprueba que una conexión esté disponible
    para activar el canal.
    """

    if not isinstance(resultado, dict):
        return False

    return (
        resultado.get("estado") == "CONECTADO"
        and resultado.get("exito") is True
    )


def activar_canal(canal):
    """
    Activa lógicamente un canal conectado.

    La publicación real se realizará en 15.5.
    """

    if not isinstance(canal, dict):
        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "detalle": "El canal no es válido."
        }

    nombre = canal.get("canal")

    if not nombre:
        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "detalle": "No se indicó el canal."
        }

    if not canal.get("conexion_activa"):
        return {
            "estado": ESTADO_BLOQUEADO,
            "exito": False,
            "canal": nombre,
            "detalle": (
                "El canal no tiene una conexión activa."
            )
        }

    return {
        "estado": ESTADO_ACTIVADO,
        "exito": True,
        "canal": nombre,
        "activo": True,
        "publicado": False,
        "detalle": (
            "El asistente fue activado "
            "para este canal."
        )
    }


def activar_canales(resultado_conexiones):
    """
    Activa todos los canales conectados.
    """

    try:

        if not validar_conexion(
            resultado_conexiones
        ):
            return {
                "estado": ESTADO_BLOQUEADO,
                "exito": False,
                "canales": [],
                "detalle": (
                    "No existen conexiones válidas "
                    "para activar."
                )
            }

        canales = resultado_conexiones.get(
            "canales",
            []
        )

        if not canales:
            return {
                "estado": ESTADO_INCOMPLETO,
                "exito": False,
                "canales": [],
                "detalle": (
                    "No existen canales para activar."
                )
            }

        resultados = []

        for canal in canales:

            resultado = activar_canal(
                canal
            )

            resultados.append(
                resultado
            )

        bloqueados = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == ESTADO_BLOQUEADO
        )

        incompletos = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == ESTADO_INCOMPLETO
        )

        errores = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == ESTADO_ERROR
        )

        activados = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == ESTADO_ACTIVADO
        )

        if errores > 0:

            estado = ESTADO_ERROR
            exito = False

        elif bloqueados > 0:

            estado = ESTADO_BLOQUEADO
            exito = False

        elif incompletos > 0:

            estado = ESTADO_INCOMPLETO
            exito = False

        elif activados == len(resultados):

            estado = ESTADO_ACTIVADO
            exito = True

        else:

            estado = ESTADO_ERROR
            exito = False

        return {
            "estado": estado,
            "exito": exito,
            "canales": resultados,
            "resumen": {
                "total": len(resultados),
                "activados": activados,
                "bloqueados": bloqueados,
                "incompletos": incompletos,
                "errores": errores
            }
        }

    except Exception as e:

        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "canales": [],
            "detalle": (
                "Error durante la activación "
                "de los canales."
            ),
            "error": str(e)
        }


def activacion_aprobada(resultado):
    """
    Comprueba si todos los canales fueron activados.
    """

    if not isinstance(resultado, dict):
        return False

    return (
        resultado.get("estado")
        == ESTADO_ACTIVADO
        and resultado.get("exito") is True
    )


def obtener_resumen_activacion(resultado):
    """
    Devuelve un resumen de 15.4.
    """

    if not isinstance(resultado, dict):

        return {
            "estado": ESTADO_ERROR,
            "exito": False
        }

    return {
        "estado": resultado.get(
            "estado",
            ESTADO_ERROR
        ),
        "exito": resultado.get(
            "exito",
            False
        ),
        "resumen": resultado.get(
            "resumen",
            {}
        ),
        "canales": resultado.get(
            "canales",
            []
        )
    }