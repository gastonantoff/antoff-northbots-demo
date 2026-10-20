from motor_preparacion_pruebas import preparar_prueba, obtener_resumen_preparacion
from motor_prueba_conocimiento import probar_conocimiento, obtener_resumen_conocimiento
from motor_prueba_inteligencia import probar_inteligencia, obtener_resumen_inteligencia
from motor_prueba_conversacion import probar_conversacion, obtener_resumen_conversacion
from motor_validacion_final import validar_asistente, obtener_resumen_validacion

ESTADO_APROBADO = "APROBADO"
ESTADO_FALLIDO = "FALLIDO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"
ESTADO_PREPARADO = "PREPARADO"


def ejecutar_estacion14(proyecto_id):
    """Ejecuta una única pasada integral de los niveles 14.1 a 14.5."""
    resultado = {"estacion": 14, "nombre": "Prueba del asistente", "proyecto_id": proyecto_id,
                 "estado": ESTADO_ERROR, "exito": False, "listo_para_estacion15": False,
                 "etapas": [], "errores": [], "advertencias": []}
    try:
        preparacion_resultado = preparar_prueba(proyecto_id)
        preparacion = preparacion_resultado.get("preparacion", {})
        resultado["etapas"].append({"nivel": "14.1", "nombre": "Preparación", "resultado": preparacion,
                                    "resumen": obtener_resumen_preparacion(preparacion_resultado)})
        if preparacion.get("estado") != ESTADO_PREPARADO:
            # BLOQUEADO describe el nivel 14.1; para la Estación completa
            # equivale a una ejecución incompleta, no a una aprobación.
            estado_preparacion = preparacion.get("estado", ESTADO_ERROR)
            resultado["estado"] = ESTADO_INCOMPLETO if estado_preparacion == "BLOQUEADO" else estado_preparacion
            resultado["errores"].extend(preparacion.get("errores", []))
            return resultado
        paquete = preparacion_resultado.get("paquete_pruebas")
        if not isinstance(paquete, dict):
            resultado["errores"].append("No se encontró un paquete de pruebas válido.")
            return resultado

        # La Estación 15 consume exactamente el paquete que 14.1 aprobó.
        # Se conserva junto al resultado de preparación para no reconstruirlo.
        preparacion["paquete_pruebas"] = paquete

        conocimiento = probar_conocimiento(paquete)
        resultado["etapas"].append({"nivel": "14.2", "nombre": "Conocimiento", "resultado": conocimiento,
                                    "resumen": obtener_resumen_conocimiento(conocimiento)})
        inteligencia = probar_inteligencia(paquete)
        resultado["etapas"].append({"nivel": "14.3", "nombre": "Inteligencia", "resultado": inteligencia,
                                    "resumen": obtener_resumen_inteligencia(inteligencia)})
        conversacion = probar_conversacion(paquete)
        resultado["etapas"].append({"nivel": "14.4", "nombre": "Conversación", "resultado": conversacion,
                                    "resumen": obtener_resumen_conversacion(conversacion)})
        validacion = validar_asistente(preparacion, conocimiento, inteligencia, conversacion)
        resultado["etapas"].append({"nivel": "14.5", "nombre": "Validación final", "resultado": validacion,
                                    "resumen": obtener_resumen_validacion(validacion)})
        resultado["estado"] = validacion.get("estado", ESTADO_ERROR)
        resultado["exito"] = validacion.get("exito", False)
        resultado["listo_para_estacion15"] = validacion.get("listo_para_estacion15", False)
        for etapa in resultado["etapas"]:
            estado = etapa["resultado"].get("estado", ESTADO_ERROR)
            mensaje = f"{etapa['nivel']} — {etapa['nombre']}"
            if estado in (ESTADO_FALLIDO, ESTADO_ERROR):
                resultado["errores"].append(f"{mensaje} {estado.lower()}.")
            elif estado == ESTADO_INCOMPLETO:
                resultado["advertencias"].append(f"{mensaje} está incompleta.")
        return resultado
    except Exception as error:
        resultado["errores"].append(f"Error de integración de Estación 14: {error}")
        return resultado


def estacion14_aprobada(resultado):
    return isinstance(resultado, dict) and resultado.get("estado") == ESTADO_APROBADO and resultado.get("exito") is True and resultado.get("listo_para_estacion15") is True


def obtener_resumen_estacion14(resultado):
    if not isinstance(resultado, dict):
        return {"estacion": 14, "estado": ESTADO_ERROR, "exito": False, "listo_para_estacion15": False,
                "etapas": [], "errores": [], "advertencias": []}
    return {"estacion": 14, "nombre": "Prueba del asistente", "proyecto_id": resultado.get("proyecto_id"),
            "estado": resultado.get("estado"), "exito": resultado.get("exito", False),
            "listo_para_estacion15": resultado.get("listo_para_estacion15", False),
            "etapas": [{"nivel": e.get("nivel"), "nombre": e.get("nombre"), "estado": e.get("resultado", {}).get("estado", ESTADO_ERROR)} for e in resultado.get("etapas", [])],
            "errores": resultado.get("errores", []), "advertencias": resultado.get("advertencias", [])}
