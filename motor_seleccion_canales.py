ESTADO_APROBADO = "APROBADO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"


CANALES_VALIDOS = {
    "whatsapp": "WhatsApp",
    "web": "Web",
    "instagram": "Instagram",
    "telegram": "Telegram",
    "facebook": "Facebook",
    "email": "Email"
}


def normalizar_canal(canal):
    """
    Normaliza el nombre de un canal.
    """

    if not isinstance(canal, str):
        return None

    canal = canal.strip().lower()

    if canal in CANALES_VALIDOS:
        return canal

    return None


def obtener_canales_disponibles(paquete):
    """
    Obtiene los canales configurados para el asistente.
    """

    if not isinstance(paquete, dict):
        return []

    datos = paquete.get("datos", {})
    configuracion = (
        paquete.get("configuracion")
        or datos.get("configuracion", {})
    )

    canales = configuracion.get("canales", [])

    if not isinstance(canales, list):
        return []

    resultado = []

    for canal in canales:

        if isinstance(canal, dict):
            nombre = (
                canal.get("codigo")
                or canal.get("nombre")
                or canal.get("tipo")
            )

        else:
            nombre = canal

        canal_normalizado = normalizar_canal(nombre)

        if canal_normalizado:
            resultado.append(
                canal_normalizado
            )

    return list(dict.fromkeys(resultado))


def seleccionar_canales(
    paquete,
    canales_solicitados=None
):
    """
    Selecciona los canales donde se instalará
    el asistente.

    Si no se especifican canales, utiliza todos
    los canales disponibles.
    """

    try:

        disponibles = obtener_canales_disponibles(
            paquete
        )

        if not disponibles:
            return {
                "estado": ESTADO_INCOMPLETO,
                "exito": False,
                "canales_disponibles": [],
                "canales_seleccionados": [],
                "detalle": (
                    "El asistente no tiene canales "
                    "configurados."
                )
            }

        # Si no se especificaron canales,
        # se seleccionan todos los disponibles.
        if canales_solicitados is None:

            seleccionados = list(
                disponibles
            )

        else:

            if not isinstance(
                canales_solicitados,
                list
            ):
                return {
                    "estado": ESTADO_ERROR,
                    "exito": False,
                    "canales_disponibles": disponibles,
                    "canales_seleccionados": [],
                    "detalle": (
                        "La selección de canales "
                        "no es válida."
                    )
                }

            seleccionados = []

            for canal in canales_solicitados:

                normalizado = normalizar_canal(
                    canal
                )

                if (
                    normalizado
                    and normalizado in disponibles
                ):
                    if normalizado not in seleccionados:
                        seleccionados.append(
                            normalizado
                        )

        if not seleccionados:

            return {
                "estado": ESTADO_INCOMPLETO,
                "exito": False,
                "canales_disponibles": disponibles,
                "canales_seleccionados": [],
                "detalle": (
                    "No se seleccionó ningún "
                    "canal válido."
                )
            }

        return {
            "estado": ESTADO_APROBADO,
            "exito": True,
            "canales_disponibles": disponibles,
            "canales_seleccionados": seleccionados,
            "detalle": (
                "Los canales fueron seleccionados "
                "correctamente."
            )
        }

    except Exception as e:

        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "canales_disponibles": [],
            "canales_seleccionados": [],
            "detalle": (
                "Error al seleccionar canales."
            ),
            "error": str(e)
        }


def canales_seleccionados_validos(resultado):
    """
    Comprueba si existe al menos un canal
    seleccionado correctamente.
    """

    if not isinstance(resultado, dict):
        return False

    return (
        resultado.get("estado")
        == ESTADO_APROBADO
        and resultado.get("exito") is True
        and bool(
            resultado.get(
                "canales_seleccionados",
                []
            )
        )
    )


def obtener_resumen_canales(resultado):
    """
    Devuelve un resumen de 15.1.
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
        "canales_disponibles": resultado.get(
            "canales_disponibles",
            []
        ),
        "canales_seleccionados": resultado.get(
            "canales_seleccionados",
            []
        )
    }
