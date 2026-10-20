
from motor_contexto import (
    crear_contexto,
    agregar_mensaje,
    actualizar_estado
)

from motor_requisitos import (
    analizar_resolucion
)

from motor_decisiones import (
    determinar_decision
)

from motor_herramientas import (
    seleccionar_herramienta
)

from motor_orquestacion import (
    crear_orquestacion,
    agregar_paso
)

from motor_autonomia import (
    crear_control_autonomia,
    autorizar_ejecucion
)


# =========================================================
# NIVEL 13.3
# CONSTRUCTOR DEL CEREBRO
# =========================================================


def crear_cerebro_base():

    return {
        "version": "1.0",

        "estado": "INICIAL",

        "intenciones": [],
        "requisitos": [],
        "capacidades": [],
        "funciones": [],
        "herramientas": [],
        "acciones": [],
        "flujos": [],

        "configuracion": {
            "max_pasos": 10,
            "max_errores": 3,
            "max_reintentos": 2
        },

        "indice_intenciones": {},
        "indice_funciones": {},
        "indice_acciones": {},
        "indice_herramientas": {},
        "indice_operaciones": {},

        "pipeline": [
            "DETECTAR_INTENCION",
            "ACTUALIZAR_CONTEXTO",
            "EVALUAR_REQUISITOS",
            "DETERMINAR_DECISION",
            "SELECCIONAR_FUNCION",
            "SELECCIONAR_ACCION",
            "SELECCIONAR_HERRAMIENTA",
            "ORQUESTAR",
            "CONTROLAR_AUTONOMIA",
            "EJECUTAR"
        ]
    }


# =========================================================
# INDICES
# =========================================================


def construir_indice_intenciones(cerebro):

    indice = {}

    for intencion in cerebro.get(
        "intenciones",
        []
    ):

        codigo = intencion.get(
            "codigo"
        )

        if not codigo:
            continue

        indice[codigo] = intencion

    cerebro["indice_intenciones"] = indice

    return cerebro


def construir_indice_funciones(cerebro):

    indice = {}

    for funcion in cerebro.get(
        "funciones",
        []
    ):

        funcion_id = funcion.get(
            "funcion_id"
        )

        if funcion_id is None:
            continue

        indice[funcion_id] = funcion

    cerebro["indice_funciones"] = indice

    return cerebro


def construir_indice_acciones(cerebro):

    indice = {}

    for accion in cerebro.get(
        "acciones",
        []
    ):

        accion_id = accion.get(
            "id"
        )

        if accion_id is None:
            continue

        indice[accion_id] = accion

    cerebro["indice_acciones"] = indice

    return cerebro


def construir_indice_herramientas(cerebro):

    indice = {}

    for herramienta in cerebro.get(
        "herramientas",
        []
    ):

        herramienta_id = herramienta.get(
            "id"
        )

        if herramienta_id is None:
            continue

        indice[herramienta_id] = herramienta

    cerebro["indice_herramientas"] = indice

    return cerebro


def construir_indice_operaciones(cerebro):

    indice = {}

    for herramienta in cerebro.get(
        "herramientas",
        []
    ):

        if not herramienta.get(
            "activo",
            False
        ):
            continue

        for accion in herramienta.get(
            "acciones",
            []
        ):

            if not accion.get(
                "activo",
                False
            ):
                continue

            operacion = accion.get(
                "operacion"
            )

            if not operacion:
                continue

            if operacion not in indice:
                indice[operacion] = []

            indice[operacion].append({
                "herramienta": herramienta,
                "accion": accion
            })

    cerebro["indice_operaciones"] = indice

    return cerebro


# =========================================================
# CONSTRUCCIÓN DEL CEREBRO
# =========================================================


def construir_cerebro(adn):

    if not adn:
        return None

    cerebro = crear_cerebro_base()

    inteligencia = adn.get(
        "inteligencia",
        {}
    )

    comportamiento = adn.get(
        "comportamiento",
        {}
    )

    cerebro["intenciones"] = inteligencia.get(
        "intenciones",
        []
    )

    cerebro["requisitos"] = inteligencia.get(
        "requisitos",
        []
    )

    cerebro["capacidades"] = inteligencia.get(
        "capacidades",
        []
    )

    cerebro["funciones"] = inteligencia.get(
        "funciones",
        []
    )

    cerebro["herramientas"] = inteligencia.get(
        "herramientas",
        []
    )

    cerebro["acciones"] = inteligencia.get(
        "acciones",
        []
    )

    cerebro["flujos"] = inteligencia.get(
        "flujos",
        []
    )

    cerebro["configuracion_ia"] = comportamiento.get(
        "configuracion_ia",
        {}
    )

    configuracion_ia = cerebro["configuracion_ia"]

    if isinstance(configuracion_ia, dict):
        autonomia = configuracion_ia.get("autonomia")

        if autonomia:
            cerebro["configuracion"]["autonomia"] = autonomia

    cerebro["personalidad"] = comportamiento.get(
        "personalidad",
        {}
    )

    cerebro = construir_indice_intenciones(
        cerebro
    )

    cerebro = construir_indice_funciones(
        cerebro
    )

    cerebro = construir_indice_acciones(
        cerebro
    )

    cerebro = construir_indice_herramientas(
        cerebro
    )

    cerebro = construir_indice_operaciones(
        cerebro
    )

    cerebro["estado"] = "CONSTRUIDO"

    return cerebro


# =========================================================
# BÚSQUEDAS
# =========================================================


def buscar_intencion_en_cerebro(
    cerebro,
    codigo
):

    return cerebro.get(
        "indice_intenciones",
        {}
    ).get(
        codigo
    )


def buscar_funcion_por_id(
    cerebro,
    funcion_id
):

    return cerebro.get(
        "indice_funciones",
        {}
    ).get(
        funcion_id
    )


def buscar_accion_por_id(
    cerebro,
    accion_id
):

    return cerebro.get(
        "indice_acciones",
        {}
    ).get(
        accion_id
    )


def buscar_herramienta_por_id(
    cerebro,
    herramienta_id
):

    return cerebro.get(
        "indice_herramientas",
        {}
    ).get(
        herramienta_id
    )


# =========================================================
# RELACIÓN FUNCIÓN → ACCIÓN
# =========================================================


def obtener_acciones_de_funcion(
    cerebro,
    funcion_id
):

    funcion = buscar_funcion_por_id(
        cerebro,
        funcion_id
    )

    if not funcion:
        return []

    acciones = []

    for accion in cerebro.get(
        "acciones",
        []
    ):

        if accion.get(
            "funcion_id"
        ) != funcion_id:
            continue

        if not accion.get(
            "activo",
            True
        ):
            continue

        acciones.append(
            accion
        )

    return acciones


# =========================================================
# SELECCIÓN DE FUNCIÓN
# =========================================================


def seleccionar_funcion(
    cerebro,
    intencion
):

    if not intencion:
        return None

    funcion_id = intencion.get(
        "funcion_id"
    )

    if funcion_id is not None:

        funcion = buscar_funcion_por_id(
            cerebro,
            funcion_id
        )

        if funcion:
            return funcion

    funciones = cerebro.get(
        "funciones",
        []
    )

    if len(funciones) == 1:
        return funciones[0]

    return None


# =========================================================
# SELECCIÓN DE ACCIÓN
# =========================================================


def seleccionar_accion(
    cerebro,
    funcion,
    operacion=None
):

    if not funcion:
        return None

    funcion_id = funcion.get(
        "funcion_id"
    )

    acciones = obtener_acciones_de_funcion(
        cerebro,
        funcion_id
    )

    if not acciones:
        return None

    if operacion:

        for accion in acciones:

            if accion.get(
                "operacion"
            ) == operacion:

                return accion

    acciones.sort(
        key=lambda accion: accion.get(
            "prioridad",
            0
        ),
        reverse=True
    )

    return acciones[0]


# =========================================================
# SELECCIÓN DE HERRAMIENTA
# =========================================================


def seleccionar_herramienta_para_accion(
    cerebro,
    accion
):

    if not accion:
        return None

    herramienta_id = accion.get(
        "herramienta_id"
    )

    if herramienta_id is not None:

        herramienta = buscar_herramienta_por_id(
            cerebro,
            herramienta_id
        )

        if herramienta:
            return herramienta

    operacion = accion.get(
        "operacion"
    )

    if operacion:

        candidatas = []

        for herramienta in cerebro.get(
            "herramientas",
            []
        ):

            if not herramienta.get(
                "activo",
                False
            ):
                continue

            for accion_herramienta in herramienta.get(
                "acciones",
                []
            ):

                if accion_herramienta.get(
                    "id"
                ) == accion.get(
                    "id"
                ):

                    candidatas.append(
                        herramienta
                    )

        if candidatas:

            return seleccionar_herramienta(
                candidatas,
                operacion
            )

    return None


# =========================================================
# ORQUESTACIÓN
# =========================================================


def preparar_orquestacion(
    objetivo,
    operacion,
    datos
):

    orquestacion = crear_orquestacion(
        objetivo=objetivo
    )

    agregar_paso(
        orquestacion=orquestacion,
        operacion=operacion,
        datos=datos
    )

    return orquestacion


# =========================================================
# AUTONOMÍA
# =========================================================


def crear_control(cerebro):

    configuracion = cerebro.get(
        "configuracion",
        {}
    )

    return crear_control_autonomia(

        max_pasos=configuracion.get(
            "max_pasos",
            10
        ),

        max_errores=configuracion.get(
            "max_errores",
            3
        ),

        max_reintentos=configuracion.get(
            "max_reintentos",
            2
        )
    )


# =========================================================
# PROCESAMIENTO PRINCIPAL
# =========================================================


def detectar_intencion_local(cerebro, mensaje):
    texto = str(mensaje or "").strip().lower()
    candidatas = []

    for intencion in cerebro.get("intenciones", []):
        if not intencion.get("activa", 1):
            continue

        coincidencias = []
        for patron in intencion.get("patrones", []):
            if not patron.get("activo", 1):
                continue
            patron_texto = str(patron.get("patron", "")).strip().lower()
            if not patron_texto:
                continue
            if patron_texto in texto:
                coincidencias.append(patron_texto)

        if coincidencias:
            puntaje = int(intencion.get("prioridad", 0) or 0) + len(coincidencias)
            candidatas.append((puntaje, intencion, coincidencias))

    if not candidatas:
        return {"estado": "INTENCION_NO_DETECTADA", "intencion": None, "confianza": 0, "alternativas": []}

    candidatas.sort(key=lambda x: x[0], reverse=True)
    puntaje, ganadora, coincidencias = candidatas[0]
    alternativas = candidatas[1:]
    confianza = 100 if not alternativas else max(0, min(100, round((puntaje - alternativas[0][0]) / max(puntaje, 1) * 100, 2)))

    intencion_resultado = dict(ganadora)
    intencion_resultado["coincidencias"] = coincidencias
    intencion_resultado["puntaje"] = puntaje

    return {
        "estado": "INTENCION_DETECTADA",
        "intencion": intencion_resultado,
        "confianza": confianza,
        "alternativas": [x[1] for x in alternativas]
    }


def seleccionar_funcion(cerebro, intencion):
    if not intencion:
        return None

    funcion_id = intencion.get("funcion_id")
    if funcion_id is not None:
        funcion = buscar_funcion_por_id(cerebro, funcion_id)
        if funcion:
            return funcion

    funciones = [f for f in cerebro.get("funciones", []) if f.get("activa", 1)]
    if len(funciones) == 1:
        return funciones[0]

    # La base actual no tiene una relación Intención -> Función.
    # Si hay varias funciones, no inventamos la relación.
    return None


def seleccionar_accion(cerebro, funcion, operacion=None):
    if not funcion:
        return None
    funcion_id = funcion.get("funcion_id")
    acciones = obtener_acciones_de_funcion(cerebro, funcion_id)
    if operacion:
        for accion in acciones:
            if accion.get("operacion") == operacion:
                return accion
    if not acciones:
        # Compatibilidad con un proyecto donde existe una sola acción ejecutable.
        acciones = [a for a in cerebro.get("acciones", []) if a.get("activo", 1)]
        if len(acciones) == 1:
            return acciones[0]
        return None
    return sorted(acciones, key=lambda a: a.get("prioridad", 0), reverse=True)[0]


def seleccionar_herramienta_para_accion(cerebro, accion):
    if not accion:
        return None
    herramienta_id = accion.get("herramienta_id")
    if herramienta_id is not None:
        herramienta = buscar_herramienta_por_id(cerebro, herramienta_id)
        if herramienta:
            return herramienta
    # La acción recolectada originalmente vive dentro de una herramienta.
    # Buscar por acción local evita depender de DB.
    for herramienta in cerebro.get("herramientas", []):
        if not herramienta.get("activo", 1):
            continue
        for accion_local in herramienta.get("acciones", []):
            if accion_local.get("id") == accion.get("id"):
                return herramienta
    return None


def procesar_mensaje(
    cerebro,
    mensaje,
    contexto=None
):
    if not cerebro:
        return {"estado": "CEREBRO_NO_EXISTE", "exito": False}
    if not mensaje or str(mensaje).strip() == "":
        return {"estado": "MENSAJE_VACIO", "exito": False}
    if contexto is None:
        contexto = crear_contexto()
    agregar_mensaje(contexto=contexto, rol="usuario", mensaje=mensaje)

    resultado_intencion = detectar_intencion_local(cerebro, mensaje)
    if resultado_intencion.get("estado") == "INTENCION_NO_DETECTADA":
        actualizar_estado(contexto, "ESPERANDO_ACLARACION")
        return {"estado": "INTENCION_NO_DETECTADA", "exito": False, "contexto": contexto, "intencion": None, "resolucion": None, "decision": determinar_decision(resultado_intencion, None), "funcion": None, "accion": None, "herramienta": None, "orquestacion": None, "autonomia": None}

    intencion = resultado_intencion.get("intencion")
    requisitos = intencion.get("requisitos", [])
    resultado_resolucion = analizar_resolucion(intencion=intencion, contexto=contexto, requisitos=requisitos)
    decision = determinar_decision(resultado_intencion, resultado_resolucion)

    if decision["tipo"] == "PEDIR_DATO":
        actualizar_estado(contexto, "ESPERANDO_DATO")
        return {"estado": "INFORMACION_INCOMPLETA", "exito": True, "contexto": contexto, "intencion": intencion, "resolucion": resultado_resolucion, "decision": decision, "funcion": None, "accion": None, "herramienta": None, "orquestacion": None, "autonomia": None}

    if decision["tipo"] != "EJECUTAR_ACCION":
        actualizar_estado(contexto, "ESPERANDO_ACLARACION")
        return {"estado": "DECISION_NO_EJECUTABLE", "exito": False, "contexto": contexto, "intencion": intencion, "resolucion": resultado_resolucion, "decision": decision, "funcion": None, "accion": None, "herramienta": None, "orquestacion": None, "autonomia": None}

    funcion = seleccionar_funcion(cerebro, intencion)
    if not funcion:
        actualizar_estado(contexto, "FUNCION_NO_ENCONTRADA")
        return {"estado": "FUNCION_NO_ENCONTRADA", "exito": False, "contexto": contexto, "intencion": intencion, "resolucion": resultado_resolucion, "decision": decision, "funcion": None, "accion": None, "herramienta": None, "orquestacion": None, "autonomia": None}

    accion = seleccionar_accion(cerebro, funcion)
    if not accion:
        actualizar_estado(contexto, "ACCION_NO_ENCONTRADA")
        return {"estado": "ACCION_NO_ENCONTRADA", "exito": False, "contexto": contexto, "intencion": intencion, "resolucion": resultado_resolucion, "decision": decision, "funcion": funcion, "accion": None, "herramienta": None, "orquestacion": None, "autonomia": None}

    herramienta = seleccionar_herramienta_para_accion(cerebro, accion)
    if not herramienta:
        actualizar_estado(contexto, "HERRAMIENTA_NO_ENCONTRADA")
        return {"estado": "HERRAMIENTA_NO_ENCONTRADA", "exito": False, "contexto": contexto, "intencion": intencion, "resolucion": resultado_resolucion, "decision": decision, "funcion": funcion, "accion": accion, "herramienta": None, "orquestacion": None, "autonomia": None}

    datos = resultado_resolucion.get("evaluacion", {}).get("disponibles", [])
    orquestacion = preparar_orquestacion(
        objetivo=funcion.get("objetivo") or funcion.get("nombre", "resolver solicitud"),
        operacion=accion.get("operacion", ""),
        datos=datos
    )

    control = crear_control(cerebro)
    autorizacion = autorizar_ejecucion(control, herramienta)

    if not autorizacion.get("autorizado", False):
        actualizar_estado(contexto, "EJECUCION_BLOQUEADA")
        return {"estado": "EJECUCION_BLOQUEADA", "exito": False, "contexto": contexto, "intencion": intencion, "resolucion": resultado_resolucion, "decision": decision, "funcion": funcion, "accion": accion, "herramienta": herramienta, "orquestacion": orquestacion, "autonomia": {"autorizacion": autorizacion}}

    actualizar_estado(contexto, "LISTO_PARA_EJECUTAR")
    return {"estado": "LISTO_PARA_EJECUTAR", "exito": True, "contexto": contexto, "intencion": intencion, "resolucion": resultado_resolucion, "decision": decision, "funcion": funcion, "accion": accion, "herramienta": herramienta, "orquestacion": orquestacion, "autonomia": {"autorizacion": autorizacion}}

