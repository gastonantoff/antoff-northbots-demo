import json
import os
from copy import deepcopy


# =========================================================
# NIVEL 13.5
# GENERADOR DEL RUNTIME
# =========================================================


BASE_ASISTENTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asistentes")


# =========================================================
# IDENTIFICACIÓN
# =========================================================


def generar_id_asistente(proyecto_id):

    return f"AST-{int(proyecto_id):06d}"


def obtener_directorio_asistente(
    asistente_id
):

    return os.path.join(
        BASE_ASISTENTES,
        asistente_id
    )


# =========================================================
# ESTRUCTURA DE DIRECTORIOS
# =========================================================


def crear_estructura_asistente(
    asistente_id
):

    directorio = obtener_directorio_asistente(
        asistente_id
    )

    recursos = os.path.join(
        directorio,
        "recursos"
    )

    os.makedirs(
        recursos,
        exist_ok=True
    )

    return {
        "directorio": directorio,
        "recursos": recursos
    }


# =========================================================
# ARCHIVOS JSON
# =========================================================


def guardar_json(
    ruta,
    datos
):

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            datos,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    return ruta


# =========================================================
# GENERACIÓN DE CONFIGURACIÓN
# =========================================================


def construir_configuracion(
    adn,
    cerebro,
    personalidad,
    asistente_id
):

    identidad = deepcopy(
        adn.get(
            "identidad",
            {}
        )
    )

    identidad["asistente_id"] = asistente_id
    identidad["id"] = asistente_id

    return {

        "asistente": identidad,

        "empresa": deepcopy(
            adn.get(
                "empresa",
                {}
            )
        ),

        "conocimiento": deepcopy(
            adn.get(
                "conocimiento",
                {}
            )
        ),

        "canales": deepcopy(
            adn.get(
                "operacion",
                {}
            ).get(
                "canales",
                []
            )
        ),

        "configuracion_ia": deepcopy(
            adn.get(
                "comportamiento",
                {}
            ).get(
                "configuracion_ia",
                {}
            )
        ),

        "version": "1.0"
    }


# =========================================================
# GENERACIÓN DEL CEREBRO
# =========================================================


def construir_configuracion_cerebro(
    cerebro
):

    if not cerebro:
        return {}

    return {

        "version": cerebro.get(
            "version",
            "1.0"
        ),

        "pipeline": deepcopy(
            cerebro.get(
                "pipeline",
                []
            )
        ),

        "intenciones": deepcopy(
            cerebro.get(
                "intenciones",
                []
            )
        ),

        "requisitos": deepcopy(
            cerebro.get(
                "requisitos",
                []
            )
        ),

        "capacidades": deepcopy(
            cerebro.get(
                "capacidades",
                []
            )
        ),

        "funciones": deepcopy(
            cerebro.get(
                "funciones",
                []
            )
        ),

        "acciones": deepcopy(
            cerebro.get(
                "acciones",
                []
            )
        ),

        "herramientas": deepcopy(
            cerebro.get(
                "herramientas",
                []
            )
        ),

        "flujos": deepcopy(
            cerebro.get(
                "flujos",
                []
            )
        ),

        "configuracion": deepcopy(
            cerebro.get(
                "configuracion",
                {}
            )
        )
    }


# =========================================================
# GENERACIÓN DE PERSONALIDAD
# =========================================================


def construir_configuracion_personalidad(
    personalidad
):

    if not personalidad:
        return {}

    perfil = {
        "nombre": personalidad.get(
            "nombre",
            ""
        ),

        "rol": personalidad.get(
            "rol",
            ""
        ),

        "objetivo": personalidad.get(
            "objetivo",
            ""
        ),

        "reglas": deepcopy(
            personalidad.get(
                "reglas_comportamiento",
                []
            )
        ),

        "instrucciones": deepcopy(
            personalidad.get(
                "instrucciones_sistema",
                []
            )
        ),

        "prompt_sistema": personalidad.get(
            "prompt_sistema",
            ""
        ),

        "configuracion_ia": deepcopy(
            personalidad.get(
                "configuracion_ia",
                {}
            )
        ),

        "estado": personalidad.get(
            "estado",
            "CONSTRUIDA"
        )
    }

    return {
        "personalidad": perfil,
        "reglas_comportamiento": deepcopy(
            personalidad.get("reglas_comportamiento", [])
        ),
        "instrucciones_sistema": deepcopy(
            personalidad.get("instrucciones_sistema", [])
        ),
        "prompt_sistema": personalidad.get("prompt_sistema", ""),
        "configuracion_ia": deepcopy(
            personalidad.get("configuracion_ia", {})
        ),
        "estado": personalidad.get("estado", "CONSTRUIDA")
    }


# =========================================================
# CÓDIGO DEL ASISTENTE
# =========================================================


def generar_codigo_asistente():

    return '''import os
import sys

RUTA_ASISTENTE = os.path.dirname(
    os.path.abspath(__file__)
)
RUTA_PROYECTO = os.path.dirname(
    RUTA_ASISTENTE
)
if RUTA_PROYECTO not in sys.path:
    sys.path.insert(0, RUTA_PROYECTO)

from runtime_asistente import ejecutar_asistente


def ejecutar(mensaje, contexto=None):
    """
    Punto de entrada del asistente personalizado.
    """

    return ejecutar_asistente(
        mensaje=mensaje,
        contexto=contexto,
        configuracion=os.path.join(
            RUTA_ASISTENTE,
            "configuracion.json"
        ),
        cerebro=os.path.join(
            RUTA_ASISTENTE,
            "cerebro.json"
        ),
        personalidad=os.path.join(
            RUTA_ASISTENTE,
            "personalidad.json"
        )
    )
'''


# =========================================================
# GENERACIÓN DE METADATOS
# =========================================================


def construir_metadatos(
    adn,
    asistente_id
):

    identidad = adn.get(
        "identidad",
        {}
    )

    return {

        "asistente_id": asistente_id,

        "proyecto_id": identidad.get(
            "proyecto_id"
        ),

        "nombre": identidad.get(
            "nombre",
            ""
        ),

        "version": "1.0",

        "estado": "GENERADO",

        "generador": "estacion_13",

        "nivel": "13.5"
    }


# =========================================================
# GENERADOR PRINCIPAL
# =========================================================


def generar_asistente(
    adn,
    cerebro,
    personalidad
):

    if not adn:

        return {
            "exito": False,
            "estado": "ADN_NO_EXISTE",
            "asistente_id": None
        }

    proyecto_id = adn.get(
        "identidad",
        {}
    ).get(
        "proyecto_id"
    )

    if not proyecto_id:

        return {
            "exito": False,
            "estado": "PROYECTO_NO_EXISTE",
            "asistente_id": None
        }

    asistente_id = generar_id_asistente(
        proyecto_id
    )

    estructura = crear_estructura_asistente(
        asistente_id
    )

    directorio = estructura[
        "directorio"
    ]

    configuracion = construir_configuracion(
        adn=adn,
        cerebro=cerebro,
        personalidad=personalidad,
        asistente_id=asistente_id
    )

    configuracion_cerebro = construir_configuracion_cerebro(
        cerebro
    )

    configuracion_personalidad = construir_configuracion_personalidad(
        personalidad
    )

    metadatos = construir_metadatos(
        adn=adn,
        asistente_id=asistente_id
    )

    ruta_configuracion = os.path.join(
        directorio,
        "configuracion.json"
    )

    ruta_cerebro = os.path.join(
        directorio,
        "cerebro.json"
    )

    ruta_personalidad = os.path.join(
        directorio,
        "personalidad.json"
    )

    ruta_metadatos = os.path.join(
        directorio,
        "metadatos.json"
    )

    ruta_asistente = os.path.join(
        directorio,
        "asistente.py"
    )

    guardar_json(
        ruta_configuracion,
        configuracion
    )

    guardar_json(
        ruta_cerebro,
        configuracion_cerebro
    )

    guardar_json(
        ruta_personalidad,
        configuracion_personalidad
    )

    guardar_json(
        ruta_metadatos,
        metadatos
    )

    with open(
        ruta_asistente,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            generar_codigo_asistente()
        )

    return {

        "exito": True,

        "estado": "GENERADO",

        "asistente_id": asistente_id,

        "directorio": directorio,

        "archivos": {

            "asistente": ruta_asistente,

            "configuracion": ruta_configuracion,

            "cerebro": ruta_cerebro,

            "personalidad": ruta_personalidad,

            "metadatos": ruta_metadatos
        }
    }