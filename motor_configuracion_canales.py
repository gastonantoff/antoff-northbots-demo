ESTADO_APROBADO = "APROBADO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"


CONFIGURACION_BASE = {
    "whatsapp": {
        "nombre": "WhatsApp",
        "requiere": [
            "numero",
            "proveedor",
            "credenciales"
        ]
    },
    "web": {
        "nombre": "Web",
        "requiere": [
            "url",
            "credenciales"
        ]
    },
    "instagram": {
        "nombre": "Instagram",
        "requiere": [
            "cuenta",
            "credenciales"
        ]
    },
    "telegram": {
        "nombre": "Telegram",
        "requiere": [
            "bot",
            "credenciales"
        ]
    },
    "facebook": {
        "nombre": "Facebook",
        "requiere": [
            "pagina",
            "credenciales"
        ]
    },
    "email": {
        "nombre": "Email",
        "requiere": [
            "direccion",
            "servidor",
            "credenciales"
        ]
    }
}


def crear_configuracion_canal(
    canal,
    datos=None
):
    """
    Crea la configuración de un canal.

    No realiza ninguna conexión externa.
    """

    if not isinstance(canal, str):
        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "detalle": "El canal no es válido."
        }

    canal = canal.strip().lower()

    if canal not in CONFIGURACION_BASE:
        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "detalle": f"Canal no soportado: {canal}"
        }

    datos = datos or {}

    requisitos = CONFIGURACION_BASE[
        canal
    ]["requiere"]

    configuracion = {
        "canal": canal,
        "nombre": CONFIGURACION_BASE[
            canal
        ]["nombre"],
        "configuracion": {},
        "requisitos": requisitos,
        "configurado": False
    }

    for requisito in requisitos:

        if requisito in datos:
            configuracion[
                "configuracion"
            ][requisito] = datos[
                requisito
            ]

    configuracion["configurado"] = all(
        requisito in configuracion["configuracion"]
        and configuracion["configuracion"][requisito]
        for requisito in requisitos
    )

    if configuracion["configurado"]:

        estado = ESTADO_APROBADO
        detalle = (
            "La configuración del canal "
            "está completa."
        )

    else:

        estado = ESTADO_INCOMPLETO
        detalle = (
            "La configuración del canal "
            "está incompleta."
        )

    return {
        "estado": estado,
        "exito": estado == ESTADO_APROBADO,
        "canal": canal,
        "configuracion": configuracion,
        "detalle": detalle
    }


def configurar_canales(
    resultado_seleccion,
    configuraciones=None
):
    """
    Configura todos los canales seleccionados
    en 15.1.

    configuraciones debe tener esta forma:

    {
        "whatsapp": {
            "numero": "...",
            "proveedor": "...",
            "credenciales": {...}
        }
    }
    """

    try:

        if not isinstance(
            resultado_seleccion,
            dict
        ):
            return {
                "estado": ESTADO_ERROR,
                "exito": False,
                "canales": [],
                "detalle": (
                    "El resultado de selección "
                    "no es válido."
                )
            }

        canales = resultado_seleccion.get(
            "canales_seleccionados",
            []
        )

        if not canales:

            return {
                "estado": ESTADO_INCOMPLETO,
                "exito": False,
                "canales": [],
                "detalle": (
                    "No existen canales "
                    "seleccionados."
                )
            }

        configuraciones = configuraciones or {}

        resultados = []

        for canal in canales:

            datos = configuraciones.get(
                canal,
                {}
            )

            resultado = crear_configuracion_canal(
                canal,
                datos
            )

            resultados.append(
                resultado
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

        if errores > 0:

            estado = ESTADO_ERROR
            exito = False

        elif incompletos > 0:

            estado = ESTADO_INCOMPLETO
            exito = False

        else:

            estado = ESTADO_APROBADO
            exito = True

        return {
            "estado": estado,
            "exito": exito,
            "canales": resultados,
            "resumen": {
                "total": len(resultados),
                "configurados": sum(
                    1
                    for resultado in resultados
                    if resultado.get(
                        "estado"
                    ) == ESTADO_APROBADO
                ),
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
                "Error al configurar los canales."
            ),
            "error": str(e)
        }


def configuracion_aprobada(resultado):
    """
    Indica si todos los canales seleccionados
    tienen configuración completa.
    """

    if not isinstance(resultado, dict):
        return False

    return (
        resultado.get("estado")
        == ESTADO_APROBADO
        and resultado.get("exito") is True
    )


def obtener_resumen_configuracion(resultado):
    """
    Devuelve un resumen de 15.2.
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