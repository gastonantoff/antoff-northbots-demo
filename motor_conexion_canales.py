ESTADO_CONECTADO = "CONECTADO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_FALLIDO = "FALLIDO"
ESTADO_ERROR = "ERROR"


def validar_configuracion_canal(canal):
    """
    Comprueba que exista una configuración
    utilizable para el canal.
    """

    if not isinstance(canal, dict):
        return False

    configuracion = canal.get(
        "configuracion",
        {}
    )

    if not isinstance(configuracion, dict):
        return False

    return bool(
        configuracion.get(
            "configurado",
            False
        )
    )


def preparar_conexion(canal):
    """
    Prepara la conexión de un canal.

    Este nivel todavía no realiza una llamada
    externa al proveedor.

    Deja preparado el contrato que utilizará
    el conector real.
    """

    if not isinstance(canal, dict):

        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "detalle": "Configuración de canal inválida."
        }

    nombre = canal.get(
        "canal"
    )

    if not nombre:

        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "detalle": "No se indicó el canal."
        }

    if not validar_configuracion_canal(
        canal
    ):

        return {
            "estado": ESTADO_INCOMPLETO,
            "exito": False,
            "canal": nombre,
            "detalle": (
                "El canal no tiene una "
                "configuración completa."
            )
        }

    return {
        "estado": ESTADO_CONECTADO,
        "exito": True,
        "canal": nombre,
        "conector": (
            f"conector_{nombre}"
        ),
        "conexion_activa": True,
        "detalle": (
            "El canal está preparado para "
            "utilizar su conector."
        )
    }


def conectar_canales(
    resultado_configuracion
):
    """
    Procesa todos los canales configurados.

    Devuelve el estado de conexión de cada uno.
    """

    try:

        if not isinstance(
            resultado_configuracion,
            dict
        ):

            return {
                "estado": ESTADO_ERROR,
                "exito": False,
                "canales": [],
                "detalle": (
                    "El resultado de configuración "
                    "no es válido."
                )
            }

        canales = resultado_configuracion.get(
            "canales",
            []
        )

        if not canales:

            return {
                "estado": ESTADO_INCOMPLETO,
                "exito": False,
                "canales": [],
                "detalle": (
                    "No existen canales "
                    "para conectar."
                )
            }

        resultados = []

        for canal in canales:

            configuracion = canal.get(
                "configuracion",
                {}
            )

            datos_canal = {
                "canal": canal.get(
                    "canal"
                ),
                "configuracion": {
                    **configuracion,
                    "configurado": canal.get(
                        "estado"
                    ) == "APROBADO"
                }
            }

            resultado = preparar_conexion(
                datos_canal
            )

            resultados.append(
                resultado
            )

        fallidos = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == ESTADO_FALLIDO
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

        conectados = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == ESTADO_CONECTADO
        )

        if errores > 0:

            estado = ESTADO_ERROR
            exito = False

        elif fallidos > 0:

            estado = ESTADO_FALLIDO
            exito = False

        elif incompletos > 0:

            estado = ESTADO_INCOMPLETO
            exito = False

        elif conectados == len(resultados):

            estado = ESTADO_CONECTADO
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
                "conectados": conectados,
                "incompletos": incompletos,
                "fallidos": fallidos,
                "errores": errores
            }
        }

    except Exception as e:

        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "canales": [],
            "detalle": (
                "Error durante la conexión "
                "de los canales."
            ),
            "error": str(e)
        }


def conexiones_aprobadas(resultado):
    """
    Indica si todos los canales están conectados.
    """

    if not isinstance(resultado, dict):
        return False

    return (
        resultado.get("estado")
        == ESTADO_CONECTADO
        and resultado.get("exito") is True
    )


def obtener_resumen_conexiones(resultado):
    """
    Devuelve un resumen de 15.3.
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