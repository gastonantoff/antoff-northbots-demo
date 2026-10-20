ESTADO_OPERANDO = "OPERANDO"
ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_BLOQUEADO = "BLOQUEADO"
ESTADO_ERROR = "ERROR"


def validar_activacion(resultado):
    """
    Comprueba que los canales hayan sido activados
    correctamente.
    """

    if not isinstance(resultado, dict):
        return False

    return (
        resultado.get("estado") == "ACTIVADO"
        and resultado.get("exito") is True
    )


def publicar_canal(canal):
    """
    Publica lógicamente el asistente en un canal
    previamente activado.

    La implementación concreta del envío/recepción
    dependerá del conector real del canal.
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

    if not canal.get("activo"):
        return {
            "estado": ESTADO_BLOQUEADO,
            "exito": False,
            "canal": nombre,
            "detalle": (
                "El canal no está activado."
            )
        }

    return {
        "estado": ESTADO_OPERANDO,
        "exito": True,
        "canal": nombre,
        "activo": True,
        "publicado": True,
        "operando": True,
        "detalle": (
            "El asistente está operativo "
            "en este canal."
        )
    }


def publicar_canales(resultado_activacion):
    """
    Publica todos los canales activados.
    """

    try:

        if not validar_activacion(
            resultado_activacion
        ):
            return {
                "estado": ESTADO_BLOQUEADO,
                "exito": False,
                "canales": [],
                "detalle": (
                    "No existen activaciones válidas "
                    "para publicar."
                )
            }

        canales = resultado_activacion.get(
            "canales",
            []
        )

        if not canales:
            return {
                "estado": ESTADO_PENDIENTE,
                "exito": False,
                "canales": [],
                "detalle": (
                    "No existen canales para publicar."
                )
            }

        resultados = []

        for canal in canales:

            resultado = publicar_canal(
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

        errores = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == ESTADO_ERROR
        )

        operando = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == ESTADO_OPERANDO
        )

        total = len(resultados)

        if errores > 0:

            estado = ESTADO_ERROR
            exito = False

        elif bloqueados > 0:

            estado = ESTADO_BLOQUEADO
            exito = False

        elif operando == total:

            estado = ESTADO_OPERANDO
            exito = True

        else:

            estado = ESTADO_PENDIENTE
            exito = False

        return {
            "estado": estado,
            "exito": exito,
            "canales": resultados,
            "resumen": {
                "total": total,
                "operando": operando,
                "bloqueados": bloqueados,
                "errores": errores
            }
        }

    except Exception as e:

        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "canales": [],
            "detalle": (
                "Error durante la publicación "
                "de los canales."
            ),
            "error": str(e)
        }


def asistente_operando(resultado):
    """
    Comprueba si el asistente está operativo
    en todos los canales.
    """

    if not isinstance(resultado, dict):
        return False

    return (
        resultado.get("estado")
        == ESTADO_OPERANDO
        and resultado.get("exito") is True
    )


def obtener_resumen_publicacion(resultado):
    """
    Devuelve un resumen de 15.5.
    """

    if not isinstance(resultado, dict):

        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "operando": False
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
        "operando": asistente_operando(
            resultado
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