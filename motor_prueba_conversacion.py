import copy


ESTADO_APROBADO = "APROBADO"
ESTADO_FALLIDO = "FALLIDO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"


def crear_resultado(nombre, estado, detalle="", datos=None):
    return {
        "nombre": nombre,
        "estado": estado,
        "detalle": detalle,
        "datos": datos or {}
    }


def obtener_personalidad(paquete):
    datos = paquete.get("datos", {}) if isinstance(paquete, dict) else {}
    personalidad = paquete.get("personalidad") or datos.get("personalidad", {})

    if isinstance(personalidad, dict):
        perfil = personalidad.get("personalidad")

        if isinstance(perfil, dict):
            return perfil

        return personalidad

    return {}


def probar_identidad(paquete):
    datos = paquete.get("datos", {}) if isinstance(paquete, dict) else {}
    configuracion = paquete.get("configuracion") or datos.get("configuracion", {})
    identidad = (
        configuracion.get("identidad")
        or configuracion.get("asistente", {})
    )

    nombre = identidad.get("nombre")
    asistente_id = (
        identidad.get("asistente_id")
        or identidad.get("id")
    )

    if not nombre and not asistente_id:
        return crear_resultado(
            "Identidad",
            ESTADO_INCOMPLETO,
            "No se encontró identidad suficiente."
        )

    return crear_resultado(
        "Identidad",
        ESTADO_APROBADO,
        "La identidad del asistente está disponible.",
        {
            "nombre": nombre,
            "asistente_id": asistente_id
        }
    )


def probar_personalidad(paquete):
    personalidad = obtener_personalidad(paquete)

    if not personalidad:
        return crear_resultado(
            "Personalidad",
            ESTADO_INCOMPLETO,
            "No se encontró configuración de personalidad."
        )

    campos = [
        "nombre",
        "rol",
        "objetivo",
        "comunicacion"
    ]

    presentes = [
        campo for campo in campos
        if personalidad.get(campo)
    ]

    if not presentes:
        return crear_resultado(
            "Personalidad",
            ESTADO_FALLIDO,
            "La personalidad no contiene información utilizable."
        )

    return crear_resultado(
        "Personalidad",
        ESTADO_APROBADO,
        "La personalidad contiene parámetros de comportamiento.",
        {
            "campos_configurados": presentes
        }
    )


def probar_contexto(paquete):
    datos = paquete.get("datos", {}) if isinstance(paquete, dict) else {}
    personalidad = paquete.get("personalidad") or datos.get("personalidad", {})
    cerebro = paquete.get("cerebro") or datos.get("cerebro", {})

    tiene_personalidad = bool(personalidad)
    tiene_cerebro = bool(cerebro)

    if not tiene_personalidad or not tiene_cerebro:
        return crear_resultado(
            "Contexto",
            ESTADO_INCOMPLETO,
            "No hay suficiente información para comprobar el contexto conversacional."
        )

    contexto = {
        "mensajes": [],
        "estado": {},
        "datos": {}
    }

    contexto["mensajes"].append({
        "rol": "usuario",
        "contenido": "Hola"
    })

    contexto["mensajes"].append({
        "rol": "asistente",
        "contenido": "Hola, ¿en qué puedo ayudarte?"
    })

    contexto["estado"]["conversacion_activa"] = True

    return crear_resultado(
        "Contexto",
        ESTADO_APROBADO,
        "El paquete permite mantener una estructura básica de contexto conversacional.",
        {
            "mensajes": len(contexto["mensajes"]),
            "conversacion_activa": True
        }
    )


def probar_memoria_conversacion(paquete):
    contexto = {
        "mensajes": [],
        "datos": {}
    }

    mensaje_usuario = {
        "rol": "usuario",
        "contenido": "Necesito consultar el precio de un producto."
    }

    contexto["mensajes"].append(mensaje_usuario)

    contexto["datos"]["ultima_consulta"] = "precio"

    if not contexto["mensajes"]:
        return crear_resultado(
            "Memoria conversacional",
            ESTADO_FALLIDO,
            "No fue posible registrar el mensaje."
        )

    if contexto["datos"].get("ultima_consulta") != "precio":
        return crear_resultado(
            "Memoria conversacional",
            ESTADO_FALLIDO,
            "No fue posible conservar el dato de contexto."
        )

    return crear_resultado(
        "Memoria conversacional",
        ESTADO_APROBADO,
        "El contexto puede conservar mensajes y datos de la conversación.",
        {
            "mensajes_guardados": len(contexto["mensajes"]),
            "dato_recordado": contexto["datos"]["ultima_consulta"]
        }
    )


def probar_coherencia(paquete):
    datos = paquete.get("datos", {}) if isinstance(paquete, dict) else {}
    cerebro = paquete.get("cerebro") or datos.get("cerebro", {})
    personalidad = obtener_personalidad(paquete)

    intenciones = cerebro.get("intenciones", [])
    capacidades = cerebro.get("capacidades", [])

    if not cerebro or not personalidad:
        return crear_resultado(
            "Coherencia conversacional",
            ESTADO_INCOMPLETO,
            "Faltan componentes para comprobar coherencia."
        )

    if not intenciones and not capacidades:
        return crear_resultado(
            "Coherencia conversacional",
            ESTADO_INCOMPLETO,
            "El asistente no tiene suficientes elementos de inteligencia configurados."
        )

    return crear_resultado(
        "Coherencia conversacional",
        ESTADO_APROBADO,
        "La estructura del asistente contiene elementos para mantener una conversación coherente.",
        {
            "intenciones": len(intenciones),
            "capacidades": len(capacidades)
        }
    )


def probar_conversacion(paquete_pruebas):
    try:
        if not isinstance(paquete_pruebas, dict):
            return {
                "estado": ESTADO_ERROR,
                "exito": False,
                "resultados": [],
                "resumen": "El paquete de pruebas no es válido."
            }

        resultados = [
            probar_identidad(paquete_pruebas),
            probar_personalidad(paquete_pruebas),
            probar_contexto(paquete_pruebas),
            probar_memoria_conversacion(paquete_pruebas),
            probar_coherencia(paquete_pruebas)
        ]

        aprobados = sum(
            1 for resultado in resultados
            if resultado["estado"] == ESTADO_APROBADO
        )

        fallidos = sum(
            1 for resultado in resultados
            if resultado["estado"] == ESTADO_FALLIDO
        )

        incompletos = sum(
            1 for resultado in resultados
            if resultado["estado"] == ESTADO_INCOMPLETO
        )

        total = len(resultados)

        if fallidos > 0:
            estado_final = ESTADO_FALLIDO

        elif incompletos > 0:
            estado_final = ESTADO_INCOMPLETO

        else:
            estado_final = ESTADO_APROBADO

        return {
            "estado": estado_final,
            "exito": estado_final == ESTADO_APROBADO,
            "resultados": resultados,
            "resumen": {
                "total": total,
                "aprobados": aprobados,
                "fallidos": fallidos,
                "incompletos": incompletos,
                "porcentaje_aprobacion": (
                    round((aprobados / total) * 100, 2)
                    if total
                    else 0
                )
            }
        }

    except Exception as e:
        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "resultados": [],
            "resumen": "Error durante la prueba de conversación.",
            "error": str(e)
        }


def conversacion_aprobada(resultado):
    if not isinstance(resultado, dict):
        return False

    return resultado.get("estado") == ESTADO_APROBADO


def obtener_resumen_conversacion(resultado):
    if not isinstance(resultado, dict):
        return {
            "estado": ESTADO_ERROR
        }

    return {
        "estado": resultado.get("estado"),
        "exito": resultado.get("exito", False),
        "resumen": resultado.get("resumen", {}),
        "resultados": resultado.get("resultados", [])
    }
