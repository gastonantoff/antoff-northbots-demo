ESTADO_APROBADO = "APROBADO"
ESTADO_FALLIDO = "FALLIDO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"


def obtener_estado(resultado):
    """
    Obtiene el estado de una etapa de pruebas.
    """
    if not isinstance(resultado, dict):
        return ESTADO_ERROR

    return resultado.get("estado", ESTADO_ERROR)


def validar_etapa(nombre, resultado):
    """
    Convierte el resultado de una etapa en un resultado
    uniforme para la validación final.
    """

    estado = obtener_estado(resultado)

    return {
        "etapa": nombre,
        "estado": estado,
        "aprobada": estado == ESTADO_APROBADO,
        "resultado": resultado
    }


def validar_preparacion(resultado):
    return validar_etapa(
        "14.1 Preparación",
        resultado
    )


def validar_conocimiento(resultado):
    return validar_etapa(
        "14.2 Conocimiento",
        resultado
    )


def validar_inteligencia(resultado):
    return validar_etapa(
        "14.3 Inteligencia",
        resultado
    )


def validar_conversacion(resultado):
    return validar_etapa(
        "14.4 Conversación",
        resultado
    )


def validar_asistente(
    resultado_preparacion,
    resultado_conocimiento,
    resultado_inteligencia,
    resultado_conversacion
):
    """
    Realiza la validación final de la Estación 14.
    """

    try:
        etapas = [
            validar_preparacion(resultado_preparacion),
            validar_conocimiento(resultado_conocimiento),
            validar_inteligencia(resultado_inteligencia),
            validar_conversacion(resultado_conversacion)
        ]

        aprobadas = sum(
            1
            for etapa in etapas
            if etapa["aprobada"]
        )

        fallidas = sum(
            1
            for etapa in etapas
            if etapa["estado"] == ESTADO_FALLIDO
        )

        incompletas = sum(
            1
            for etapa in etapas
            if etapa["estado"] == ESTADO_INCOMPLETO
        )

        errores = sum(
            1
            for etapa in etapas
            if etapa["estado"] == ESTADO_ERROR
        )

        total = len(etapas)

        # Cualquier error bloquea la validación.
        if errores > 0:
            estado_final = ESTADO_ERROR
            listo_para_estacion15 = False

        # Una prueba fallida bloquea el asistente.
        elif fallidas > 0:
            estado_final = ESTADO_FALLIDO
            listo_para_estacion15 = False

        # Una prueba incompleta también bloquea el paso.
        elif incompletas > 0:
            estado_final = ESTADO_INCOMPLETO
            listo_para_estacion15 = False

        # Solo pasa si todas las etapas fueron aprobadas.
        else:
            estado_final = ESTADO_APROBADO
            listo_para_estacion15 = True

        porcentaje = (
            round((aprobadas / total) * 100, 2)
            if total
            else 0
        )

        return {
            "estado": estado_final,
            "exito": estado_final == ESTADO_APROBADO,
            "listo_para_estacion15": listo_para_estacion15,

            "resumen": {
                "total_etapas": total,
                "aprobadas": aprobadas,
                "fallidas": fallidas,
                "incompletas": incompletas,
                "errores": errores,
                "porcentaje_aprobacion": porcentaje
            },

            "etapas": etapas
        }

    except Exception as e:

        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "listo_para_estacion15": False,

            "resumen": {
                "total_etapas": 0,
                "aprobadas": 0,
                "fallidas": 0,
                "incompletas": 0,
                "errores": 1,
                "porcentaje_aprobacion": 0
            },

            "etapas": [],

            "error": str(e)
        }


def asistente_aprobado(resultado):
    """
    Indica si el asistente superó toda la Estación 14.
    """

    if not isinstance(resultado, dict):
        return False

    return (
        resultado.get("estado") == ESTADO_APROBADO
        and resultado.get("listo_para_estacion15") is True
    )


def obtener_resumen_validacion(resultado):
    """
    Devuelve un resumen simple para mostrar en interfaz
    o utilizar desde la Estación 15.
    """

    if not isinstance(resultado, dict):
        return {
            "estado": ESTADO_ERROR,
            "exito": False,
            "listo_para_estacion15": False
        }

    return {
        "estado": resultado.get("estado"),
        "exito": resultado.get("exito", False),
        "listo_para_estacion15": resultado.get(
            "listo_para_estacion15",
            False
        ),
        "resumen": resultado.get(
            "resumen",
            {}
        )
    }