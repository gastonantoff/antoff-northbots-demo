from copy import deepcopy


# =========================================================
# NIVEL 13.4
# CONSTRUCTOR DE PERSONALIDAD
# =========================================================


def crear_personalidad_base():

    return {
        "nombre": "",
        "rol": "",
        "objetivo": "",

        "comunicacion": "",
        "iniciativa": "",
        "longitud_respuestas": "",

        "emojis": False,

        "restricciones": "",
        "despedida": "",

        "configuracion_ia": {},

        "reglas_comportamiento": [],

        "instrucciones_sistema": [],

        "estado": "INICIAL"
    }


# =========================================================
# NORMALIZACIÓN
# =========================================================


def normalizar_valor(valor, valor_defecto=""):

    if valor is None:
        return valor_defecto

    if isinstance(valor, str):
        return valor.strip()

    return valor


def normalizar_booleano(valor):

    if isinstance(valor, bool):
        return valor

    if valor is None:
        return False

    if isinstance(valor, int):
        return valor == 1

    if isinstance(valor, str):

        valor_normalizado = (
            valor
            .strip()
            .lower()
        )

        return valor_normalizado in [
            "1",
            "true",
            "si",
            "sí",
            "yes",
            "activo",
            "habilitado"
        ]

    return False


# =========================================================
# CONSTRUCCIÓN DEL PERFIL
# =========================================================


def construir_personalidad(adn):

    if not adn:
        return None

    comportamiento = adn.get(
        "comportamiento",
        {}
    )

    personalidad_bd = comportamiento.get(
        "personalidad",
        {}
    )

    configuracion_ia = comportamiento.get(
        "configuracion_ia",
        {}
    )

    personalidad = crear_personalidad_base()

    personalidad["nombre"] = normalizar_valor(
        personalidad_bd.get(
            "nombre"
        )
    )

    personalidad["rol"] = normalizar_valor(
        personalidad_bd.get(
            "rol"
        )
    )

    personalidad["objetivo"] = normalizar_valor(
        personalidad_bd.get(
            "objetivo"
        )
    )

    personalidad["comunicacion"] = normalizar_valor(
        personalidad_bd.get(
            "comunicacion"
        )
    )

    personalidad["iniciativa"] = normalizar_valor(
        personalidad_bd.get(
            "iniciativa"
        )
    )

    personalidad["longitud_respuestas"] = normalizar_valor(
        personalidad_bd.get(
            "longitud_respuestas"
        )
    )

    personalidad["emojis"] = normalizar_booleano(
        personalidad_bd.get(
            "emojis"
        )
    )

    personalidad["restricciones"] = normalizar_valor(
        personalidad_bd.get(
            "restricciones"
        )
    )

    personalidad["despedida"] = normalizar_valor(
        personalidad_bd.get(
            "despedida"
        )
    )

    personalidad["configuracion_ia"] = deepcopy(
        configuracion_ia
    )

    personalidad["estado"] = "CONSTRUIDA"

    return personalidad


# =========================================================
# REGLAS DE COMPORTAMIENTO
# =========================================================


def construir_reglas_comportamiento(
    personalidad
):

    if not personalidad:
        return []

    reglas = []

    comunicacion = personalidad.get(
        "comunicacion"
    )

    if comunicacion:
        reglas.append({
            "tipo": "COMUNICACION",
            "regla": comunicacion
        })

    iniciativa = personalidad.get(
        "iniciativa"
    )

    if iniciativa:
        reglas.append({
            "tipo": "INICIATIVA",
            "regla": iniciativa
        })

    longitud = personalidad.get(
        "longitud_respuestas"
    )

    if longitud:
        reglas.append({
            "tipo": "LONGITUD",
            "regla": longitud
        })

    if personalidad.get(
        "emojis",
        False
    ):

        reglas.append({
            "tipo": "EMOJIS",
            "regla": "Puede utilizar emojis cuando sean apropiados."
        })

    restricciones = personalidad.get(
        "restricciones"
    )

    if restricciones:
        reglas.append({
            "tipo": "RESTRICCIONES",
            "regla": restricciones
        })

    despedida = personalidad.get(
        "despedida"
    )

    if despedida:
        reglas.append({
            "tipo": "DESPEDIDA",
            "regla": despedida
        })

    return reglas


# =========================================================
# INSTRUCCIONES DEL SISTEMA
# =========================================================


def construir_instrucciones_sistema(
    personalidad,
    empresa=None
):

    instrucciones = []

    if not personalidad:
        return instrucciones

    nombre = personalidad.get(
        "nombre"
    )

    rol = personalidad.get(
        "rol"
    )

    objetivo = personalidad.get(
        "objetivo"
    )

    if nombre:
        instrucciones.append(
            f"Tu nombre es {nombre}."
        )

    if rol:
        instrucciones.append(
            f"Tu rol es: {rol}."
        )

    if objetivo:
        instrucciones.append(
            f"Tu objetivo principal es: {objetivo}."
        )

    comunicacion = personalidad.get(
        "comunicacion"
    )

    if comunicacion:
        instrucciones.append(
            f"Forma de comunicación: {comunicacion}."
        )

    iniciativa = personalidad.get(
        "iniciativa"
    )

    if iniciativa:
        instrucciones.append(
            f"Nivel de iniciativa: {iniciativa}."
        )

    longitud = personalidad.get(
        "longitud_respuestas"
    )

    if longitud:
        instrucciones.append(
            f"Longitud de las respuestas: {longitud}."
        )

    if personalidad.get(
        "emojis",
        False
    ):

        instrucciones.append(
            "Puedes utilizar emojis cuando sean apropiados."
        )

    restricciones = personalidad.get(
        "restricciones"
    )

    if restricciones:
        instrucciones.append(
            f"Restricciones: {restricciones}."
        )

    despedida = personalidad.get(
        "despedida"
    )

    if despedida:
        instrucciones.append(
            f"Despedida configurada: {despedida}."
        )

    if empresa:

        nombre_empresa = empresa.get(
            "nombre"
        )

        rubro = empresa.get(
            "rubro"
        )

        if nombre_empresa:
            instrucciones.append(
                f"La empresa a la que representas es {nombre_empresa}."
            )

        if rubro:
            instrucciones.append(
                f"El rubro de la empresa es {rubro}."
            )

    return instrucciones


# =========================================================
# CONSTRUCTOR COMPLETO
# =========================================================


def preparar_personalidad(
    adn
):

    if not adn:
        return None

    personalidad = construir_personalidad(
        adn
    )

    empresa = adn.get(
        "empresa"
    )

    reglas = construir_reglas_comportamiento(
        personalidad
    )

    instrucciones = construir_instrucciones_sistema(
        personalidad,
        empresa
    )

    personalidad["reglas_comportamiento"] = reglas

    personalidad["instrucciones_sistema"] = instrucciones

    personalidad["estado"] = "LISTA"

    return personalidad


# =========================================================
# OBTENER INSTRUCCIONES
# =========================================================


def obtener_instrucciones_sistema(
    personalidad
):

    if not personalidad:
        return []

    return personalidad.get(
        "instrucciones_sistema",
        []
    )


def obtener_reglas_comportamiento(
    personalidad
):

    if not personalidad:
        return []

    return personalidad.get(
        "reglas_comportamiento",
        []
    )


# =========================================================
# GENERAR PROMPT DE SISTEMA
# =========================================================


def generar_prompt_sistema(
    personalidad
):

    instrucciones = obtener_instrucciones_sistema(
        personalidad
    )

    if not instrucciones:
        return ""

    return "\n".join(
        f"- {instruccion}"
        for instruccion in instrucciones
    )


# =========================================================
# PERFIL FINAL
# =========================================================


def obtener_perfil_personalidad(
    adn
):

    personalidad = preparar_personalidad(
        adn
    )

    if not personalidad:
        return None

    return {
        "nombre": personalidad.get(
            "nombre"
        ),

        "rol": personalidad.get(
            "rol"
        ),

        "objetivo": personalidad.get(
            "objetivo"
        ),

        "reglas": personalidad.get(
            "reglas_comportamiento",
            []
        ),

        "instrucciones": personalidad.get(
            "instrucciones_sistema",
            []
        ),

        "prompt_sistema": generar_prompt_sistema(
            personalidad
        ),

        "configuracion_ia": deepcopy(
            personalidad.get(
                "configuracion_ia",
                {}
            )
        ),

        "estado": personalidad.get(
            "estado"
        )
    }