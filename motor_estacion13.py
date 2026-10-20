import os
import json
from copy import deepcopy

from motor_recolector import recolectar_proyecto
from motor_adn import construir_adn, completar_adn, validar_adn
from motor_cerebro import construir_cerebro
from motor_personalidad import preparar_personalidad
from motor_generador import generar_asistente
from motor_ensamblador import ensamblar_desde_archivos
from motor_activacion import activar_asistente, guardar_activacion
from db_manager import guardar_asistente


def fabricar_asistente(proyecto_id):
    resultado = {
        "estacion": 13,
        "estado": "INICIANDO",
        "exito": False,
        "etapas": {},
        "errores": [],
        "advertencias": [],
    }

    # 13.1 Recolector
    proyecto = recolectar_proyecto(proyecto_id)
    if not proyecto:
        resultado["estado"] = "ERROR_RECOLECTOR"
        resultado["errores"].append("No se pudo recolectar el proyecto.")
        return resultado
    resultado["etapas"]["13.1"] = "COMPLETADO"

    # 13.2 ADN
    adn = construir_adn(proyecto)
    validacion_adn = validar_adn(adn)
    if not validacion_adn.get("valido"):
        resultado["estado"] = "ERROR_ADN"
        resultado["errores"].extend(validacion_adn.get("errores", []))
        return resultado
    resultado["etapas"]["13.2"] = "COMPLETADO"

    # 13.3 Cerebro
    cerebro = construir_cerebro(adn)
    if not cerebro:
        resultado["estado"] = "ERROR_CEREBRO"
        resultado["errores"].append("No se pudo construir el cerebro.")
        return resultado
    resultado["etapas"]["13.3"] = "COMPLETADO"

    # 13.4 Personalidad
    personalidad = preparar_personalidad(adn)
    if not personalidad:
        resultado["estado"] = "ERROR_PERSONALIDAD"
        resultado["errores"].append("No se pudo construir la personalidad.")
        return resultado
    resultado["etapas"]["13.4"] = "COMPLETADO"

    # 13.5 Generación
    generado = generar_asistente(adn, cerebro, personalidad)
    if not generado.get("exito"):
        resultado["estado"] = "ERROR_GENERACION"
        resultado["errores"].append(generado.get("estado", "GENERACION_FALLIDA"))
        return resultado
    resultado["etapas"]["13.5"] = "COMPLETADO"
    resultado["asistente_id"] = generado["asistente_id"]
    resultado["directorio"] = os.path.abspath(generado["directorio"])
    resultado["archivos"] = {
        k: os.path.abspath(v) for k, v in generado["archivos"].items()
    }

    # 13.6 Ensamblaje desde los artefactos reales
    ensamblado = ensamblar_desde_archivos(
        configuracion_path=resultado["archivos"]["configuracion"],
        cerebro_path=resultado["archivos"]["cerebro"],
        personalidad_path=resultado["archivos"]["personalidad"],
        asistente_path=resultado["archivos"]["asistente"],
    )
    resultado["ensamblador"] = ensamblado
    resultado["advertencias"].extend(ensamblado.get("advertencias", []))
    if not ensamblado.get("validado"):
        resultado["estado"] = "ERROR_ENSAMBLADO"
        resultado["errores"].extend(ensamblado.get("errores", []))
        return resultado
    resultado["etapas"]["13.6"] = "COMPLETADO"

    # 13.7 Activación / entrega a pruebas
    activacion = activar_asistente(
        ensamblador=ensamblado,
        asistente_id=generado["asistente_id"],
        nombre=adn.get("identidad", {}).get("nombre", ""),
        ruta_runtime=resultado["archivos"]["asistente"],
    )
    resultado["activacion"] = activacion
    resultado["advertencias"].extend(activacion.get("advertencias", []))

    if not activacion.get("listo_para_pruebas"):
        resultado["estado"] = "ERROR_ACTIVACION"
        resultado["errores"].extend(activacion.get("errores", []))
        return resultado

    ruta_activacion = guardar_activacion(
        activacion,
        resultado["directorio"]
    )
    resultado["archivos"]["activacion"] = os.path.abspath(ruta_activacion)

    # Registrar en la aplicación que este proyecto ya tiene un asistente
    # generado y entregado a pruebas.
    guardar_asistente(
        proyecto_id=proyecto_id,
        nombre=adn.get("identidad", {}).get("nombre", ""),
        instrucciones=personalidad.get("prompt_sistema", ""),
        configuracion=json.dumps(
            {
                "asistente_id": generado["asistente_id"],
                "directorio": resultado["directorio"],
                "archivos": resultado["archivos"],
                "estado": "LISTO_PARA_PRUEBAS"
            },
            ensure_ascii=False
        ),
        estado="Listo para pruebas"
    )

    resultado["etapas"]["13.7"] = "COMPLETADO"
    resultado["estado"] = "LISTO_PARA_PRUEBAS"
    resultado["exito"] = True

    return resultado
