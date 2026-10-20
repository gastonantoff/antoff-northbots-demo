import os
import json


# ============================================================
# ESTADOS
# ============================================================

ESTADO_ENSAMBLADO = "ENSAMBLADO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"


# ============================================================
# BASE DEL ENSAMBLADOR
# ============================================================

def crear_ensamblador_base():
    return {
        "estado": ESTADO_INCOMPLETO,
        "validado": False,
        "errores": [],
        "advertencias": [],
        "componentes": {},
        "rutas": {},
        "resumen": {}
    }


# ============================================================
# VALIDAR ARCHIVOS
# ============================================================

def validar_archivo(ruta, nombre, errores):
    if not ruta:
        errores.append(f"No se indicó la ruta de {nombre}.")
        return False

    if not os.path.exists(ruta):
        errores.append(
            f"No existe el archivo de {nombre}: {ruta}"
        )
        return False

    return True


# ============================================================
# VALIDAR JSON
# ============================================================

def validar_json(ruta, nombre, errores):
    if not validar_archivo(ruta, nombre, errores):
        return None

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except json.JSONDecodeError as error:
        errores.append(
            f"El archivo {nombre} no contiene un JSON válido: {error}"
        )

    except Exception as error:
        errores.append(
            f"No se pudo leer {nombre}: {error}"
        )

    return None


# ============================================================
# VALIDAR CONFIGURACIÓN
# ============================================================

def validar_configuracion(configuracion, errores):
    if not configuracion:
        errores.append(
            "La configuración del asistente está vacía."
        )
        return False

    if "asistente" not in configuracion:
        errores.append(
            "La configuración no contiene identidad del asistente."
        )
        return False

    return True


# ============================================================
# VALIDAR CEREBRO
# ============================================================

def validar_cerebro(cerebro, errores, advertencias):
    if not cerebro:
        errores.append(
            "El cerebro del asistente está vacío."
        )
        return False

    campos = [
        "intenciones",
        "funciones",
        "acciones",
        "herramientas"
    ]

    for campo in campos:
        if campo not in cerebro:
            advertencias.append(
                f"El cerebro no contiene el bloque '{campo}'."
            )

    return True


# ============================================================
# VALIDAR PERSONALIDAD
# ============================================================

def validar_personalidad(personalidad, errores):
    if not personalidad:
        errores.append(
            "La personalidad del asistente está vacía."
        )
        return False

    if "personalidad" not in personalidad:
        # Compatibilidad con artefactos de versiones anteriores.
        if not personalidad.get("nombre") and not personalidad.get("prompt_sistema"):
            errores.append(
                "No existe el bloque de personalidad."
            )
            return False

    return True


# ============================================================
# VALIDAR IDENTIDAD
# ============================================================

def validar_identidad(configuracion, errores):
    asistente = configuracion.get("asistente", {})

    if not asistente.get("id") and not asistente.get("asistente_id"):
        errores.append(
            "El asistente no tiene ID."
        )

    if not asistente.get("nombre"):
        errores.append(
            "El asistente no tiene nombre."
        )


# ============================================================
# VALIDAR COMPONENTES DEL CEREBRO
# ============================================================

def validar_componentes_cerebro(
    cerebro,
    errores,
    advertencias
):
    intenciones = cerebro.get("intenciones", [])
    funciones = cerebro.get("funciones", [])
    acciones = cerebro.get("acciones", [])
    herramientas = cerebro.get("herramientas", [])

    if not intenciones:
        advertencias.append(
            "El asistente no tiene intenciones configuradas."
        )

    if not funciones:
        advertencias.append(
            "El asistente no tiene funciones configuradas."
        )

    if not acciones:
        advertencias.append(
            "El asistente no tiene acciones configuradas."
        )

    if not herramientas:
        advertencias.append(
            "El asistente no tiene herramientas configuradas."
        )

    return {
        "intenciones": len(intenciones),
        "funciones": len(funciones),
        "acciones": len(acciones),
        "herramientas": len(herramientas)
    }


# ============================================================
# VALIDAR RUTAS DEL ASISTENTE
# ============================================================

def validar_rutas(
    rutas,
    errores
):
    validar_archivo(
        rutas.get("configuracion"),
        "configuración",
        errores
    )

    validar_archivo(
        rutas.get("cerebro"),
        "cerebro",
        errores
    )

    validar_archivo(
        rutas.get("personalidad"),
        "personalidad",
        errores
    )

    validar_archivo(
        rutas.get("asistente"),
        "runtime del asistente",
        errores
    )


# ============================================================
# ENSAMBLAR
# ============================================================

def ensamblar_asistente(
    configuracion,
    cerebro,
    personalidad,
    rutas=None
):
    ensamblador = crear_ensamblador_base()

    errores = ensamblador["errores"]
    advertencias = ensamblador["advertencias"]

    # --------------------------------------------------------
    # VALIDACIONES PRINCIPALES
    # --------------------------------------------------------

    validar_configuracion(
        configuracion,
        errores
    )

    validar_cerebro(
        cerebro,
        errores,
        advertencias
    )

    validar_personalidad(
        personalidad,
        errores
    )

    if configuracion:
        validar_identidad(
            configuracion,
            errores
        )

    # --------------------------------------------------------
    # COMPONENTES
    # --------------------------------------------------------

    if cerebro:
        componentes = validar_componentes_cerebro(
            cerebro,
            errores,
            advertencias
        )
    else:
        componentes = {}

    ensamblador["componentes"] = componentes

    # --------------------------------------------------------
    # RUTAS
    # --------------------------------------------------------

    if rutas:
        validar_rutas(
            rutas,
            errores
        )

        ensamblador["rutas"] = rutas

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    asistente = {}

    if configuracion:
        asistente = configuracion.get(
            "asistente",
            {}
        )

    ensamblador["resumen"] = {
        "id": asistente.get("id"),
        "nombre": asistente.get("nombre"),
        "cantidad_intenciones": componentes.get(
            "intenciones",
            0
        ),
        "cantidad_funciones": componentes.get(
            "funciones",
            0
        ),
        "cantidad_acciones": componentes.get(
            "acciones",
            0
        ),
        "cantidad_herramientas": componentes.get(
            "herramientas",
            0
        ),
        "cantidad_errores": len(errores),
        "cantidad_advertencias": len(advertencias)
    }

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    if errores:
        ensamblador["estado"] = ESTADO_ERROR
        ensamblador["validado"] = False

    else:
        ensamblador["estado"] = ESTADO_ENSAMBLADO
        ensamblador["validado"] = True

    return ensamblador


# ============================================================
# ENSAMBLAR DESDE ARCHIVOS
# ============================================================

def ensamblar_desde_archivos(
    configuracion_path,
    cerebro_path,
    personalidad_path,
    asistente_path=None
):
    errores = []

    configuracion = validar_json(
        configuracion_path,
        "configuración",
        errores
    )

    cerebro = validar_json(
        cerebro_path,
        "cerebro",
        errores
    )

    personalidad = validar_json(
        personalidad_path,
        "personalidad",
        errores
    )

    rutas = {
        "configuracion": configuracion_path,
        "cerebro": cerebro_path,
        "personalidad": personalidad_path,
        "asistente": asistente_path
    }

    if errores:
        resultado = crear_ensamblador_base()

        resultado["estado"] = ESTADO_ERROR
        resultado["validado"] = False
        resultado["errores"] = errores
        resultado["rutas"] = rutas

        return resultado

    return ensamblar_asistente(
        configuracion=configuracion,
        cerebro=cerebro,
        personalidad=personalidad,
        rutas=rutas
    )


# ============================================================
# VALIDACIÓN RÁPIDA
# ============================================================

def asistente_esta_ensamblado(resultado):
    if not resultado:
        return False

    return (
        resultado.get("estado") == ESTADO_ENSAMBLADO
        and resultado.get("validado") is True
    )


# ============================================================
# RESUMEN
# ============================================================

def obtener_resumen_ensamblador(resultado):
    if not resultado:
        return {}

    return {
        "estado": resultado.get("estado"),
        "validado": resultado.get("validado"),
        "errores": resultado.get("errores", []),
        "advertencias": resultado.get("advertencias", []),
        "resumen": resultado.get("resumen", {})
    }