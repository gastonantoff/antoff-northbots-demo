import os
import json
from datetime import datetime


# ============================================================
# ESTADOS
# ============================================================

ESTADO_LISTO_PRUEBAS = "LISTO_PARA_PRUEBAS"
ESTADO_BLOQUEADO = "BLOQUEADO"
ESTADO_ERROR = "ERROR"


# ============================================================
# BASE DE ACTIVACIÓN
# ============================================================

def crear_activacion_base():
    return {
        "estado": ESTADO_BLOQUEADO,
        "activo": False,
        "listo_para_pruebas": False,
        "asistente_id": None,
        "nombre": None,
        "fecha_activacion": None,
        "componentes": {},
        "rutas": {},
        "errores": [],
        "advertencias": []
    }


# ============================================================
# VALIDAR ENSAMBLAJE
# ============================================================

def validar_ensamblaje(ensamblador, errores):
    if not ensamblador:
        errores.append(
            "No existe información del ensamblador."
        )
        return False

    if not ensamblador.get("validado"):
        errores.append(
            "El asistente no fue validado por el ensamblador."
        )
        return False

    if ensamblador.get("estado") != "ENSAMBLADO":
        errores.append(
            "El asistente no se encuentra en estado ENSAMBLADO."
        )
        return False

    return True


# ============================================================
# VALIDAR RUNTIME
# ============================================================

def validar_runtime(ruta_runtime, errores):
    if not ruta_runtime:
        errores.append(
            "No se indicó el runtime del asistente."
        )
        return False

    if not os.path.exists(ruta_runtime):
        errores.append(
            f"No existe el runtime del asistente: {ruta_runtime}"
        )
        return False

    return True


# ============================================================
# VALIDAR COMPONENTES
# ============================================================

def validar_componentes(
    ensamblador,
    errores,
    advertencias
):
    componentes = ensamblador.get(
        "componentes",
        {}
    )

    if componentes.get("intenciones", 0) == 0:
        advertencias.append(
            "El asistente no tiene intenciones configuradas."
        )

    if componentes.get("funciones", 0) == 0:
        advertencias.append(
            "El asistente no tiene funciones configuradas."
        )

    if componentes.get("acciones", 0) == 0:
        advertencias.append(
            "El asistente no tiene acciones configuradas."
        )

    if componentes.get("herramientas", 0) == 0:
        advertencias.append(
            "El asistente no tiene herramientas configuradas."
        )

    return componentes


# ============================================================
# CREAR PAQUETE DE PRUEBAS
# ============================================================

def crear_paquete_pruebas(
    ensamblador,
    asistente_id,
    nombre
):
    componentes = ensamblador.get(
        "componentes",
        {}
    )

    return {
        "asistente_id": asistente_id,
        "nombre": nombre,
        "estado": ESTADO_LISTO_PRUEBAS,
        "origen": "ESTACION_13",
        "estacion_siguiente": 14,

        "objetivo": (
            "Validar conocimiento, inteligencia, "
            "conversación y funcionamiento del asistente."
        ),

        "componentes": componentes,

        "pruebas": {
            "conocimiento": False,
            "inteligencia": False,
            "conversacion": False,
            "validacion_final": False
        },

        "fecha_entrega": datetime.now().isoformat()
    }


# ============================================================
# ACTIVAR
# ============================================================

def activar_asistente(
    ensamblador,
    asistente_id,
    nombre,
    ruta_runtime=None
):
    activacion = crear_activacion_base()

    errores = activacion["errores"]
    advertencias = activacion["advertencias"]

    # --------------------------------------------------------
    # VALIDAR ENSAMBLAJE
    # --------------------------------------------------------

    if not validar_ensamblaje(
        ensamblador,
        errores
    ):
        activacion["estado"] = ESTADO_ERROR
        return activacion

    # --------------------------------------------------------
    # VALIDAR RUNTIME
    # --------------------------------------------------------

    if ruta_runtime:
        validar_runtime(
            ruta_runtime,
            errores
        )

    # --------------------------------------------------------
    # COMPONENTES
    # --------------------------------------------------------

    componentes = validar_componentes(
        ensamblador,
        errores,
        advertencias
    )

    # --------------------------------------------------------
    # IDENTIDAD
    # --------------------------------------------------------

    if not asistente_id:
        errores.append(
            "No se indicó el ID del asistente."
        )

    if not nombre:
        errores.append(
            "No se indicó el nombre del asistente."
        )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    if errores:
        activacion["estado"] = ESTADO_ERROR
        activacion["activo"] = False
        activacion["listo_para_pruebas"] = False

        return activacion

    # --------------------------------------------------------
    # ACTIVACIÓN
    # --------------------------------------------------------

    activacion["estado"] = ESTADO_LISTO_PRUEBAS
    activacion["activo"] = True
    activacion["listo_para_pruebas"] = True
    activacion["asistente_id"] = asistente_id
    activacion["nombre"] = nombre
    activacion["fecha_activacion"] = datetime.now().isoformat()
    activacion["componentes"] = componentes

    if ruta_runtime:
        activacion["rutas"]["runtime"] = ruta_runtime

    # --------------------------------------------------------
    # PAQUETE PARA ESTACIÓN 14
    # --------------------------------------------------------

    activacion["paquete_pruebas"] = crear_paquete_pruebas(
        ensamblador=ensamblador,
        asistente_id=asistente_id,
        nombre=nombre
    )

    return activacion


# ============================================================
# GUARDAR ESTADO DE ACTIVACIÓN
# ============================================================

def guardar_activacion(
    activacion,
    ruta_asistente
):
    if not ruta_asistente:
        return None

    os.makedirs(
        ruta_asistente,
        exist_ok=True
    )

    ruta = os.path.join(
        ruta_asistente,
        "activacion.json"
    )

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            activacion,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    return ruta


# ============================================================
# VERIFICAR SI ESTÁ LISTO PARA PRUEBAS
# ============================================================

def esta_listo_para_pruebas(activacion):
    if not activacion:
        return False

    return (
        activacion.get("estado")
        == ESTADO_LISTO_PRUEBAS
        and
        activacion.get("activo") is True
        and
        activacion.get("listo_para_pruebas") is True
    )


# ============================================================
# RESUMEN
# ============================================================

def obtener_resumen_activacion(activacion):
    if not activacion:
        return {}

    return {
        "asistente_id": activacion.get(
            "asistente_id"
        ),
        "nombre": activacion.get(
            "nombre"
        ),
        "estado": activacion.get(
            "estado"
        ),
        "activo": activacion.get(
            "activo"
        ),
        "listo_para_pruebas": activacion.get(
            "listo_para_pruebas"
        ),
        "fecha_activacion": activacion.get(
            "fecha_activacion"
        ),
        "errores": activacion.get(
            "errores",
            []
        ),
        "advertencias": activacion.get(
            "advertencias",
            []
        )
    }