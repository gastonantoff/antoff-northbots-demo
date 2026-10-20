from copy import deepcopy


def crear_adn_base():
    return {
        "version_adn": "1.0",

        "identidad": {
            "asistente_id": None,
            "proyecto_id": None,
            "nombre": "",
            "cliente": "",
            "estado": ""
        },

        "empresa": {},

        "comportamiento": {
            "personalidad": {},
            "configuracion_ia": {}
        },

        "conocimiento": {
            "catalogo": [],
            "conocimiento_general": []
        },

        "inteligencia": {
            "capacidades": [],
            "funciones": [],
            "intenciones": [],
            "herramientas": [],
            "acciones": [],
            "requisitos": [],
            "patrones": [],
            "flujos": []
        },

        "operacion": {
            "accesos": [],
            "canales": [],
            "autonomia": {},
            "memoria": {}
        },

        "metadatos": {
            "fuente": "estacion_13",
            "nivel": "13.2",
            "estado": "CONSTRUIDO"
        }
    }


def construir_adn(proyecto_completo):
    if not proyecto_completo:
        return None

    adn = crear_adn_base()

    proyecto = proyecto_completo.get(
        "proyecto"
    )

    empresa = proyecto_completo.get(
        "empresa"
    )

    personalidad = proyecto_completo.get(
        "personalidad"
    )

    configuracion_ia = proyecto_completo.get(
        "configuracion_ia"
    )

    catalogo = proyecto_completo.get(
        "catalogo",
        []
    )

    conocimiento = proyecto_completo.get(
        "conocimiento",
        []
    )

    capacidades = proyecto_completo.get(
        "capacidades",
        []
    )

    funciones = proyecto_completo.get(
        "funciones",
        []
    )

    intenciones = proyecto_completo.get(
        "intenciones",
        []
    )

    herramientas = proyecto_completo.get(
        "herramientas",
        []
    )

    capacidades_detalladas = proyecto_completo.get(
        "capacidades_detalladas",
        []
    )

    flujos = proyecto_completo.get(
        "flujos",
        []
    )

    accesos = proyecto_completo.get(
        "accesos",
        []
    )

    canales = proyecto_completo.get(
        "canales",
        []
    )

    if proyecto:
        adn["identidad"] = {
            "asistente_id": None,
            "proyecto_id": proyecto.get("id"),
            "nombre": proyecto.get("nombre", ""),
            "cliente": proyecto.get("cliente", ""),
            "estado": proyecto.get("estado", "")
        }

    if empresa:
        adn["empresa"] = deepcopy(
            empresa
        )

    adn["comportamiento"]["personalidad"] = deepcopy(
        personalidad or {}
    )

    adn["comportamiento"]["configuracion_ia"] = deepcopy(
        configuracion_ia or {}
    )

    adn["conocimiento"]["catalogo"] = deepcopy(
        catalogo
    )

    adn["conocimiento"]["conocimiento_general"] = deepcopy(
        conocimiento
    )

    adn["inteligencia"] = {
        "capacidades": deepcopy(
            capacidades
        ),

        "funciones": deepcopy(
            funciones
        ),

        "intenciones": deepcopy(
            intenciones
        ),

        "herramientas": deepcopy(
            herramientas
        ),

        "acciones": [],
        
        "requisitos": [],

        "patrones": [],

        "flujos": deepcopy(
            flujos
        )
    }

    for intencion in intenciones:

        requisitos = intencion.get(
            "requisitos",
            []
        )

        patrones = intencion.get(
            "patrones",
            []
        )

        adn["inteligencia"]["requisitos"].extend(
            deepcopy(requisitos)
        )

        adn["inteligencia"]["patrones"].extend(
            deepcopy(patrones)
        )

    for herramienta in herramientas:

        acciones = herramienta.get(
            "acciones",
            []
        )

        adn["inteligencia"]["acciones"].extend(
            deepcopy(acciones)
        )

    adn["inteligencia"]["capacidades_detalladas"] = deepcopy(
        capacidades_detalladas
    )

    adn["operacion"]["accesos"] = deepcopy(
        accesos
    )

    adn["operacion"]["canales"] = deepcopy(
        canales
    )

    adn["operacion"]["autonomia"] = {}

    adn["operacion"]["memoria"] = {}

    return adn


def completar_adn(adn, asistente_id):
    if not adn:
        return None

    adn["identidad"]["asistente_id"] = asistente_id

    return adn


def validar_adn(adn):
    if not adn:
        return {
            "valido": False,
            "errores": [
                "ADN_NO_EXISTE"
            ]
        }

    errores = []

    if not adn.get("identidad"):
        errores.append(
            "FALTA_IDENTIDAD"
        )

    if not adn["identidad"].get("proyecto_id"):
        errores.append(
            "FALTA_PROYECTO"
        )

    if not adn.get("empresa"):
        errores.append(
            "FALTA_EMPRESA"
        )

    if "comportamiento" not in adn:
        errores.append(
            "FALTA_COMPORTAMIENTO"
        )

    if "conocimiento" not in adn:
        errores.append(
            "FALTA_CONOCIMIENTO"
        )

    if "inteligencia" not in adn:
        errores.append(
            "FALTA_INTELIGENCIA"
        )

    if "operacion" not in adn:
        errores.append(
            "FALTA_OPERACION"
        )

    return {
        "valido": len(errores) == 0,
        "errores": errores
    }


def obtener_resumen_adn(adn):
    if not adn:
        return None

    return {
        "asistente_id": adn["identidad"].get(
            "asistente_id"
        ),

        "proyecto_id": adn["identidad"].get(
            "proyecto_id"
        ),

        "nombre": adn["identidad"].get(
            "nombre"
        ),

        "cantidad_catalogo": len(
            adn["conocimiento"].get(
                "catalogo",
                []
            )
        ),

        "cantidad_conocimiento": len(
            adn["conocimiento"].get(
                "conocimiento_general",
                []
            )
        ),

        "cantidad_capacidades": len(
            adn["inteligencia"].get(
                "capacidades",
                []
            )
        ),

        "cantidad_funciones": len(
            adn["inteligencia"].get(
                "funciones",
                []
            )
        ),

        "cantidad_intenciones": len(
            adn["inteligencia"].get(
                "intenciones",
                []
            )
        ),

        "cantidad_requisitos": len(
            adn["inteligencia"].get(
                "requisitos",
                []
            )
        ),

        "cantidad_patrones": len(
            adn["inteligencia"].get(
                "patrones",
                []
            )
        ),

        "cantidad_herramientas": len(
            adn["inteligencia"].get(
                "herramientas",
                []
            )
        ),

        "cantidad_acciones": len(
            adn["inteligencia"].get(
                "acciones",
                []
            )
        ),

        "cantidad_flujos": len(
            adn["inteligencia"].get(
                "flujos",
                []
            )
        ),

        "cantidad_canales": len(
            adn["operacion"].get(
                "canales",
                []
            )
        )
    }