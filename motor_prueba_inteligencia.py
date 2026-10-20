import json


ESTADO_APROBADO = "APROBADO"
ESTADO_FALLIDO = "FALLIDO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"


def crear_prueba_inteligencia_base():
    """
    Crea la estructura base del nivel 14.3.
    """

    return {
        "estacion": 14,
        "nivel": "14.3",
        "nombre": "Prueba de inteligencia",
        "estado": ESTADO_INCOMPLETO,

        "pruebas": {
            "intenciones": {
                "estado": ESTADO_INCOMPLETO,
                "cantidad": 0,
                "detalles": [],
            },

            "requisitos": {
                "estado": ESTADO_INCOMPLETO,
                "cantidad": 0,
                "detalles": [],
            },

            "decisiones": {
                "estado": ESTADO_INCOMPLETO,
                "detalles": [],
            },

            "funciones": {
                "estado": ESTADO_INCOMPLETO,
                "cantidad": 0,
                "detalles": [],
            },

            "acciones": {
                "estado": ESTADO_INCOMPLETO,
                "cantidad": 0,
                "detalles": [],
            },

            "herramientas": {
                "estado": ESTADO_INCOMPLETO,
                "cantidad": 0,
                "detalles": [],
            },

            "orquestacion": {
                "estado": ESTADO_INCOMPLETO,
                "detalles": [],
            },

            "autonomia": {
                "estado": ESTADO_INCOMPLETO,
                "detalles": [],
            },
        },

        "resumen": {
            "pruebas_totales": 0,
            "pruebas_aprobadas": 0,
            "pruebas_fallidas": 0,
            "pruebas_incompletas": 0,
        },

        "errores": [],
        "advertencias": [],
    }


def obtener_lista(datos, *claves):
    """
    Obtiene la primera lista encontrada entre las claves indicadas.
    """

    if not isinstance(datos, dict):
        return []

    for clave in claves:

        valor = datos.get(clave)

        if isinstance(valor, list):
            return valor

    return []


def obtener_diccionario(datos, *claves):
    """
    Obtiene el primer diccionario encontrado.
    """

    if not isinstance(datos, dict):
        return {}

    for clave in claves:

        valor = datos.get(clave)

        if isinstance(valor, dict):
            return valor

    return {}


def tiene_contenido(valor):
    """
    Determina si existe información utilizable.
    """

    if valor is None:
        return False

    if isinstance(valor, str):
        return bool(valor.strip())

    if isinstance(valor, list):
        return len(valor) > 0

    if isinstance(valor, dict):
        return len(valor) > 0

    return True


def probar_intenciones(resultado, cerebro):
    """
    Comprueba que el cerebro tenga intenciones configuradas.
    """

    prueba = resultado["pruebas"]["intenciones"]

    intenciones = obtener_lista(
        cerebro,
        "intenciones",
    )

    prueba["cantidad"] = len(intenciones)

    if not intenciones:

        prueba["estado"] = ESTADO_INCOMPLETO

        prueba["detalles"].append(
            "El cerebro no tiene intenciones configuradas."
        )

        resultado["advertencias"].append(
            "No existen intenciones disponibles "
            "para realizar una prueba de detección."
        )

        return

    intenciones_validas = 0

    for intencion in intenciones:

        if not isinstance(intencion, dict):
            continue

        nombre = intencion.get("nombre")

        codigo = intencion.get("codigo")

        patrones = intencion.get(
            "patrones",
            [],
        )

        if (
            tiene_contenido(nombre)
            or tiene_contenido(codigo)
        ):

            if isinstance(patrones, list):
                intenciones_validas += 1

    if intenciones_validas == 0:

        prueba["estado"] = ESTADO_FALLIDO

        prueba["detalles"].append(
            "Existen intenciones, pero no contienen "
            "una estructura utilizable."
        )

        return

    prueba["estado"] = ESTADO_APROBADO

    prueba["detalles"].append(
        f"El cerebro contiene {len(intenciones)} intenciones."
    )

    prueba["detalles"].append(
        f"{intenciones_validas} intenciones tienen "
        "información identificable."
    )


def probar_requisitos(resultado, cerebro):
    """
    Comprueba la estructura de requisitos de las intenciones.
    """

    prueba = resultado["pruebas"]["requisitos"]

    intenciones = obtener_lista(
        cerebro,
        "intenciones",
    )

    total_requisitos = 0
    intenciones_con_requisitos = 0

    for intencion in intenciones:

        if not isinstance(intencion, dict):
            continue

        requisitos = obtener_lista(
            intencion,
            "requisitos",
        )

        if requisitos:

            intenciones_con_requisitos += 1
            total_requisitos += len(requisitos)

    prueba["cantidad"] = total_requisitos

    if not intenciones:

        prueba["estado"] = ESTADO_INCOMPLETO

        prueba["detalles"].append(
            "No hay intenciones sobre las cuales "
            "evaluar requisitos."
        )

        return

    if total_requisitos == 0:

        prueba["estado"] = ESTADO_INCOMPLETO

        prueba["detalles"].append(
            "Las intenciones no tienen requisitos configurados."
        )

        resultado["advertencias"].append(
            "No existen requisitos configurados "
            "para las intenciones."
        )

        return

    prueba["estado"] = ESTADO_APROBADO

    prueba["detalles"].append(
        f"Se encontraron {total_requisitos} requisitos "
        f"en {intenciones_con_requisitos} intenciones."
    )


def probar_decisiones(resultado, cerebro):
    """
    Comprueba que el cerebro tenga definida la lógica
    de decisión necesaria para continuar una interacción.
    """

    prueba = resultado["pruebas"]["decisiones"]

    decisiones = obtener_diccionario(
        cerebro,
        "decisiones",
        "decision",
        "motor_decisiones",
    )

    if decisiones:

        prueba["estado"] = ESTADO_APROBADO

        prueba["detalles"].append(
            "Existe configuración de decisiones "
            "en el cerebro."
        )

        return

    pipeline = obtener_lista(
        cerebro,
        "pipeline",
        "flujo",
        "etapas",
    )

    if pipeline:

        nombres = [
            str(item).lower()
            for item in pipeline
        ]

        tiene_decision = any(
            "decision" in item
            for item in nombres
        )

        if tiene_decision:

            prueba["estado"] = ESTADO_APROBADO

            prueba["detalles"].append(
                "El pipeline del cerebro incluye "
                "una etapa de decisión."
            )

            return

    prueba["estado"] = ESTADO_INCOMPLETO

    prueba["detalles"].append(
        "No se encontró una configuración explícita "
        "del motor de decisiones."
    )

    resultado["advertencias"].append(
        "La configuración del cerebro no expone "
        "una estructura explícita de decisiones."
    )


def probar_funciones(resultado, cerebro):
    """
    Comprueba que existan funciones operativas.
    """

    prueba = resultado["pruebas"]["funciones"]

    funciones = obtener_lista(
        cerebro,
        "funciones",
    )

    prueba["cantidad"] = len(funciones)

    if not funciones:

        prueba["estado"] = ESTADO_INCOMPLETO

        prueba["detalles"].append(
            "El cerebro no tiene funciones configuradas."
        )

        resultado["advertencias"].append(
            "No existen funciones disponibles "
            "para la prueba de inteligencia."
        )

        return

    validas = 0

    for funcion in funciones:

        if not isinstance(funcion, dict):
            continue

        nombre = funcion.get("nombre")

        if tiene_contenido(nombre):
            validas += 1

    if validas == 0:

        prueba["estado"] = ESTADO_FALLIDO

        prueba["detalles"].append(
            "Las funciones existen, pero no tienen "
            "información identificable."
        )

        return

    prueba["estado"] = ESTADO_APROBADO

    prueba["detalles"].append(
        f"El cerebro contiene {len(funciones)} funciones."
    )


def probar_acciones(resultado, cerebro):
    """
    Comprueba que las funciones tengan acciones
    utilizables cuando estén configuradas.
    """

    prueba = resultado["pruebas"]["acciones"]

    acciones = obtener_lista(
        cerebro,
        "acciones",
    )

    prueba["cantidad"] = len(acciones)

    if not acciones:

        prueba["estado"] = ESTADO_INCOMPLETO

        prueba["detalles"].append(
            "El cerebro no tiene acciones configuradas."
        )

        resultado["advertencias"].append(
            "No existen acciones disponibles "
            "para ejecutar funciones."
        )

        return

    validas = 0

    for accion in acciones:

        if not isinstance(accion, dict):
            continue

        nombre = accion.get("nombre")

        operacion = accion.get("operacion")

        if (
            tiene_contenido(nombre)
            or tiene_contenido(operacion)
        ):
            validas += 1

    if validas == 0:

        prueba["estado"] = ESTADO_FALLIDO

        prueba["detalles"].append(
            "Las acciones existen, pero no contienen "
            "información utilizable."
        )

        return

    prueba["estado"] = ESTADO_APROBADO

    prueba["detalles"].append(
        f"El cerebro contiene {len(acciones)} acciones."
    )


def probar_herramientas(resultado, cerebro):
    """
    Comprueba la existencia de herramientas y su relación
    con acciones cuando esa información está disponible.
    """

    prueba = resultado["pruebas"]["herramientas"]

    herramientas = obtener_lista(
        cerebro,
        "herramientas",
    )

    acciones = obtener_lista(
        cerebro,
        "acciones",
    )

    if not herramientas:

        prueba["estado"] = ESTADO_INCOMPLETO

        prueba["detalles"].append(
            "El cerebro no tiene herramientas configuradas."
        )

        resultado["advertencias"].append(
            "No existen herramientas disponibles."
        )

        return

    herramientas_validas = 0

    for herramienta in herramientas:

        if not isinstance(herramienta, dict):
            continue

        nombre = herramienta.get("nombre")

        if tiene_contenido(nombre):
            herramientas_validas += 1

    if herramientas_validas == 0:

        prueba["estado"] = ESTADO_FALLIDO

        prueba["detalles"].append(
            "Las herramientas existen, pero no tienen "
            "información identificable."
        )

        return

    relaciones = 0

    for accion in acciones:

        if not isinstance(accion, dict):
            continue

        if tiene_contenido(
            accion.get("herramienta_id")
        ):

            relaciones += 1

    prueba["estado"] = ESTADO_APROBADO

    prueba["detalles"].append(
        f"El cerebro contiene {len(herramientas)} herramientas."
    )

    if relaciones:

        prueba["detalles"].append(
            f"Se encontraron {relaciones} relaciones "
            "acción → herramienta."
        )

    else:

        prueba["detalles"].append(
            "No se encontraron relaciones explícitas "
            "acción → herramienta."
        )


def probar_orquestacion(resultado, cerebro):
    """
    Comprueba la estructura de orquestación.
    """

    prueba = resultado["pruebas"]["orquestacion"]

    orquestacion = obtener_diccionario(
        cerebro,
        "orquestacion",
        "orquestador",
    )

    pipeline = obtener_lista(
        cerebro,
        "pipeline",
    )

    flujos = obtener_lista(
        cerebro,
        "flujos",
    )

    if orquestacion:

        prueba["estado"] = ESTADO_APROBADO

        prueba["detalles"].append(
            "Existe configuración de orquestación."
        )

        return

    if pipeline:

        prueba["estado"] = ESTADO_APROBADO

        prueba["detalles"].append(
            "Existe un pipeline de procesamiento."
        )

        return

    if flujos:

        prueba["estado"] = ESTADO_APROBADO

        prueba["detalles"].append(
            f"Existen {len(flujos)} flujos configurados."
        )

        return

    prueba["estado"] = ESTADO_INCOMPLETO

    prueba["detalles"].append(
        "No se encontró estructura de orquestación."
    )

    resultado["advertencias"].append(
        "El cerebro no expone una estructura "
        "de orquestación."
    )


def probar_autonomia(resultado, cerebro):
    """
    Comprueba la presencia de información de autonomía.
    """

    prueba = resultado["pruebas"]["autonomia"]

    autonomia = obtener_diccionario(
        cerebro,
        "autonomia",
    )

    configuracion = obtener_diccionario(
        cerebro,
        "configuracion",
    )

    if autonomia:

        prueba["estado"] = ESTADO_APROBADO

        prueba["detalles"].append(
            "Existe configuración de autonomía."
        )

        return

    if configuracion:

        autonomia_config = configuracion.get(
            "autonomia"
        )

        if tiene_contenido(autonomia_config):

            prueba["estado"] = ESTADO_APROBADO

            prueba["detalles"].append(
                "Existe configuración de autonomía "
                "dentro de la configuración del cerebro."
            )

            return

    prueba["estado"] = ESTADO_INCOMPLETO

    prueba["detalles"].append(
        "No existe una configuración explícita "
        "de autonomía en el cerebro."
    )

    resultado["advertencias"].append(
        "No se encontró configuración explícita "
        "de autonomía."
    )


def calcular_resumen(resultado):
    """
    Calcula el resumen de todas las pruebas.
    """

    pruebas = resultado["pruebas"]

    total = 0
    aprobadas = 0
    fallidas = 0
    incompletas = 0

    for prueba in pruebas.values():

        total += 1

        estado = prueba.get("estado")

        if estado == ESTADO_APROBADO:

            aprobadas += 1

        elif estado == ESTADO_FALLIDO:

            fallidas += 1

        else:

            incompletas += 1

    resultado["resumen"] = {
        "pruebas_totales": total,
        "pruebas_aprobadas": aprobadas,
        "pruebas_fallidas": fallidas,
        "pruebas_incompletas": incompletas,
    }


def determinar_estado_final(resultado):
    """
    Determina el resultado global de 14.3.
    """

    resumen = resultado["resumen"]

    if resumen["pruebas_fallidas"] > 0:

        resultado["estado"] = ESTADO_FALLIDO

        return

    if resumen["pruebas_incompletas"] > 0:

        resultado["estado"] = ESTADO_INCOMPLETO

        return

    resultado["estado"] = ESTADO_APROBADO


def probar_inteligencia(paquete_pruebas):
    """
    Ejecuta el nivel 14.3 utilizando el cerebro real
    producido por la Estación 13.
    """

    resultado = crear_prueba_inteligencia_base()

    try:

        if not paquete_pruebas:

            resultado["estado"] = ESTADO_ERROR

            resultado["errores"].append(
                "No existe paquete de pruebas."
            )

            return resultado

        if paquete_pruebas.get(
            "estado_preparacion"
        ) != "PREPARADO":

            resultado["estado"] = ESTADO_ERROR

            resultado["errores"].append(
                "El asistente no fue preparado "
                "correctamente por 14.1."
            )

            return resultado

        cerebro = paquete_pruebas.get(
            "datos",
            {},
        ).get(
            "cerebro"
        )

        if not isinstance(cerebro, dict):

            resultado["estado"] = ESTADO_ERROR

            resultado["errores"].append(
                "No existe un cerebro válido "
                "para realizar la prueba."
            )

            return resultado

        probar_intenciones(
            resultado,
            cerebro,
        )

        probar_requisitos(
            resultado,
            cerebro,
        )

        probar_decisiones(
            resultado,
            cerebro,
        )

        probar_funciones(
            resultado,
            cerebro,
        )

        probar_acciones(
            resultado,
            cerebro,
        )

        probar_herramientas(
            resultado,
            cerebro,
        )

        probar_orquestacion(
            resultado,
            cerebro,
        )

        probar_autonomia(
            resultado,
            cerebro,
        )

        calcular_resumen(
            resultado
        )

        determinar_estado_final(
            resultado
        )

        return resultado

    except Exception as error:

        resultado["estado"] = ESTADO_ERROR

        resultado["errores"].append(
            f"Error general en la prueba de inteligencia: {error}"
        )

        return resultado


def inteligencia_aprobada(resultado):
    """
    Indica si el nivel 14.3 fue aprobado.
    """

    if not resultado:
        return False

    return resultado.get(
        "estado"
    ) == ESTADO_APROBADO


def obtener_resumen_inteligencia(resultado):
    """
    Devuelve un resumen para las siguientes etapas.
    """

    if not resultado:

        return {
            "estacion": 14,
            "nivel": "14.3",
            "estado": ESTADO_ERROR,
            "errores": [
                "No existe resultado de la prueba."
            ],
        }

    return {
        "estacion": 14,
        "nivel": "14.3",
        "estado": resultado.get(
            "estado"
        ),
        "resumen": resultado.get(
            "resumen",
            {},
        ),
        "pruebas": resultado.get(
            "pruebas",
            {},
        ),
        "errores": resultado.get(
            "errores",
            [],
        ),
        "advertencias": resultado.get(
            "advertencias",
            [],
        ),
    }