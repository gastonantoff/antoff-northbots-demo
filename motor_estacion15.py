"""
STATION 15 — INSTALACIÓN DEL ASISTENTE

Une:
15.1 Selección de canales
15.2 Configuración de canales
15.3 Conexión de canales
15.4 Activación de canales
15.5 Publicación / operación
"""

from motor_seleccion_canales import (
    seleccionar_canales,
    canales_seleccionados_validos,
)

from motor_configuracion_canales import (
    configurar_canales,
    configuracion_aprobada,
)

from motor_conexion_canales import (
    conectar_canales,
    conexiones_aprobadas,
)

from motor_activacion_canales import (
    activar_canales,
    activacion_aprobada,
)

from motor_publicacion_canales import (
    publicar_canales,
    asistente_operando,
)


ESTADO_OPERANDO = "OPERANDO"
ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_BLOQUEADO = "BLOQUEADO"
ESTADO_ERROR = "ERROR"


def crear_resultado():
    """
    Crea la estructura general del resultado de la estación.
    """

    return {
        "estacion": 15,
        "nombre": "Instalación del asistente",
        "estado": ESTADO_PENDIENTE,
        "exito": False,
        "etapas": [],
        "errores": [],
        "advertencias": [],
        "asistente_operando": False,
    }


def registrar_etapa(resultado, nivel, nombre, etapa_resultado):
    """
    Registra una etapa ejecutada.
    """

    resultado["etapas"].append({
        "nivel": nivel,
        "nombre": nombre,
        "estado": etapa_resultado.get("estado"),
        "exito": etapa_resultado.get("exito", False),
        "resultado": etapa_resultado,
    })


def ejecutar_estacion15(
    proyecto_id,
    resultado_estacion14=None,
    canales_solicitados=None,
    configuraciones=None,
):
    """
    Ejecuta la estación completa:

    15.1 Selección
    15.2 Configuración
    15.3 Conexión
    15.4 Activación
    15.5 Publicación

    La estación 15 requiere que el asistente haya sido aprobado
    por la estación 14.
    """

    resultado = crear_resultado()

    try:

        # ==========================================================
        # VERIFICAR ESTACIÓN 14
        # ==========================================================

        if resultado_estacion14 is None:

            resultado["errores"].append(
                "La estación 15 requiere un resultado aprobado de la estación 14."
            )

            resultado["estado"] = ESTADO_BLOQUEADO

            return resultado

        if resultado_estacion14.get("estado") != "APROBADO":

            resultado["errores"].append(
                "El asistente no está aprobado para instalación."
            )

            resultado["estado"] = ESTADO_BLOQUEADO

            return resultado

        # ==========================================================
        # OBTENER PAQUETE DE PRUEBAS
        # ==========================================================

        etapas_14 = resultado_estacion14.get("etapas", [])

        preparacion = None

        for etapa in etapas_14:

            if etapa.get("nivel") == "14.1":

                preparacion = etapa.get("resultado")
                break

        if not preparacion:

            resultado["errores"].append(
                "No se encontró la preparación de pruebas de la estación 14."
            )

            resultado["estado"] = ESTADO_BLOQUEADO

            return resultado

        paquete_pruebas = preparacion.get("paquete_pruebas")

        if not paquete_pruebas:

            resultado["errores"].append(
                "No se encontró el paquete de pruebas del asistente."
            )

            resultado["estado"] = ESTADO_BLOQUEADO

            return resultado

        # ==========================================================
        # 15.1 — SELECCIÓN DE CANALES
        # ==========================================================

        etapa_151 = seleccionar_canales(
            paquete_pruebas,
            canales_solicitados,
        )

        registrar_etapa(
            resultado,
            "15.1",
            "Selección de canales",
            etapa_151,
        )

        if not canales_seleccionados_validos(etapa_151):

            resultado["errores"].append(
                "La selección de canales no es válida."
            )

            resultado["estado"] = ESTADO_BLOQUEADO

            return resultado

        # ==========================================================
        # 15.2 — CONFIGURACIÓN DE CANALES
        # ==========================================================

        etapa_152 = configurar_canales(
            etapa_151,
            configuraciones,
        )

        registrar_etapa(
            resultado,
            "15.2",
            "Configuración de canales",
            etapa_152,
        )

        if not configuracion_aprobada(etapa_152):

            resultado["errores"].append(
                "La configuración de los canales está incompleta."
            )

            resultado["estado"] = ESTADO_PENDIENTE

            return resultado

        # ==========================================================
        # 15.3 — CONEXIÓN
        # ==========================================================

        etapa_153 = conectar_canales(
            etapa_152,
        )

        registrar_etapa(
            resultado,
            "15.3",
            "Conexión de canales",
            etapa_153,
        )

        if not conexiones_aprobadas(etapa_153):

            resultado["errores"].append(
                "No fue posible preparar las conexiones de los canales."
            )

            resultado["estado"] = ESTADO_BLOQUEADO

            return resultado

        # ==========================================================
        # 15.4 — ACTIVACIÓN
        # ==========================================================

        etapa_154 = activar_canales(
            etapa_153,
        )

        registrar_etapa(
            resultado,
            "15.4",
            "Activación de canales",
            etapa_154,
        )

        if not activacion_aprobada(etapa_154):

            resultado["errores"].append(
                "Los canales no pudieron ser activados."
            )

            resultado["estado"] = ESTADO_BLOQUEADO

            return resultado

        # ==========================================================
        # 15.5 — PUBLICACIÓN / OPERACIÓN
        # ==========================================================

        etapa_155 = publicar_canales(
            etapa_154,
        )

        registrar_etapa(
            resultado,
            "15.5",
            "Publicación y operación",
            etapa_155,
        )

        if not asistente_operando(etapa_155):

            resultado["errores"].append(
                "El asistente no quedó en estado operativo."
            )

            resultado["estado"] = ESTADO_PENDIENTE

            return resultado

        # ==========================================================
        # INSTALACIÓN COMPLETADA
        # ==========================================================

        resultado["estado"] = ESTADO_OPERANDO
        resultado["exito"] = True
        resultado["asistente_operando"] = True

        return resultado

    except Exception as e:

        resultado["estado"] = ESTADO_ERROR

        resultado["errores"].append(
            f"Error inesperado en estación 15: {str(e)}"
        )

        return resultado


def estacion15_aprobada(resultado):
    """
    Determina si la estación 15 terminó correctamente.
    """

    if not resultado:
        return False

    return (
        resultado.get("estado") == ESTADO_OPERANDO
        and resultado.get("exito") is True
        and resultado.get("asistente_operando") is True
    )


def obtener_resumen_estacion15(resultado):
    """
    Genera un resumen legible de la estación.
    """

    if not resultado:

        return {
            "estado": ESTADO_ERROR,
            "mensaje": "No existe resultado de estación 15.",
        }

    etapas = []

    for etapa in resultado.get("etapas", []):

        etapas.append({
            "nivel": etapa.get("nivel"),
            "nombre": etapa.get("nombre"),
            "estado": etapa.get("estado"),
            "exito": etapa.get("exito"),
        })

    return {
        "estacion": 15,
        "nombre": "Instalación del asistente",
        "estado": resultado.get("estado"),
        "exito": resultado.get("exito"),
        "asistente_operando": resultado.get(
            "asistente_operando",
            False,
        ),
        "etapas": etapas,
        "errores": resultado.get("errores", []),
        "advertencias": resultado.get("advertencias", []),
    }