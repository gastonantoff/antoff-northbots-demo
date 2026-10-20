import re
import unicodedata

from db_manager import (
    obtener_intenciones,
    obtener_patrones_intencion
)


def normalizar_texto(texto):

    if not texto:
        return ""

    # Convertir a minúsculas
    texto = texto.lower()

    # Eliminar acentos
    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    # Eliminar signos de puntuación
    texto = re.sub(
        r"[^\w\s]",
        " ",
        texto
    )

    # Eliminar espacios repetidos
    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def evaluar_patron(
    mensaje,
    patron,
    tipo
):

    mensaje_normalizado = normalizar_texto(
        mensaje
    )

    patron_normalizado = normalizar_texto(
        patron
    )

    if not patron_normalizado:
        return False

    # Coincidencia por frase
    if tipo == "FRASE":

        return (
            patron_normalizado
            in mensaje_normalizado
        )

    # Coincidencia por palabra clave
    if tipo == "PALABRA_CLAVE":

        palabras = mensaje_normalizado.split()

        return (
            patron_normalizado
            in palabras
        )

    return False


def detectar_intenciones(mensaje):

    resultados = []

    intenciones = obtener_intenciones()

    for intencion in intenciones:

        intencion_id = intencion[0]

        activa = intencion[8]

        # Ignorar intenciones inactivas
        if activa != 1:
            continue

        patrones = obtener_patrones_intencion(
            intencion_id
        )

        coincidencias = []

        for patron in patrones:

            patron_texto = patron[2]
            tipo = patron[3]
            prioridad = patron[4]
            activo = patron[5]

            # Ignorar patrones inactivos
            if activo != 1:
                continue

            coincide = evaluar_patron(
                mensaje=mensaje,
                patron=patron_texto,
                tipo=tipo
            )

            if coincide:

                coincidencias.append({
                    "patron": patron_texto,
                    "tipo": tipo,
                    "prioridad": prioridad
                })

        if coincidencias:

            resultados.append({
                "intencion_id": intencion_id,
                "nombre": intencion[1],
                "codigo": intencion[2],
                "prioridad": intencion[5],
                "coincidencias": coincidencias
            })

    return resultados


def calcular_puntaje_intencion(resultado):

    prioridad_intencion = resultado["prioridad"]

    coincidencias = resultado["coincidencias"]

    puntaje = prioridad_intencion

    for coincidencia in coincidencias:

        puntaje += coincidencia["prioridad"]

        # Cada coincidencia encontrada suma
        # un punto adicional
        puntaje += 1

    return puntaje


def calcular_confianza(
    ganadora,
    alternativas
):

    puntaje_ganador = ganadora["puntaje"]

    # Si solo existe una intención candidata,
    # por ahora consideramos confianza máxima.
    if not alternativas:

        return 100

    puntaje_segunda = alternativas[0]["puntaje"]

    # Evitar problemas matemáticos
    if puntaje_ganador <= 0:

        return 0

    diferencia = (
        puntaje_ganador
        - puntaje_segunda
    )

    confianza = (
        diferencia
        / puntaje_ganador
    ) * 100

    # Mantener el resultado entre 0 y 100
    confianza = max(
        0,
        min(
            100,
            round(confianza, 2)
        )
    )

    return confianza


def seleccionar_intencion(mensaje):

    mensaje_normalizado = normalizar_texto(
        mensaje
    )

    resultados = detectar_intenciones(
        mensaje
    )

    # No se detectó ninguna intención
    if not resultados:

        return {
            "mensaje_original": mensaje,

            "mensaje_normalizado": (
                mensaje_normalizado
            ),

            "intencion": None,

            "confianza": 0,

            "alternativas": [],

            "estado": (
                "INTENCION_NO_DETECTADA"
            )
        }

    # Calcular puntajes
    for resultado in resultados:

        resultado["puntaje"] = (
            calcular_puntaje_intencion(
                resultado
            )
        )

    # Ordenar de mayor a menor puntaje
    resultados_ordenados = sorted(
        resultados,
        key=lambda resultado: (
            resultado["puntaje"]
        ),
        reverse=True
    )

    ganadora = resultados_ordenados[0]

    alternativas = resultados_ordenados[1:]

    confianza = calcular_confianza(
        ganadora=ganadora,
        alternativas=alternativas
    )

    return {
        "mensaje_original": mensaje,

        "mensaje_normalizado": (
            mensaje_normalizado
        ),

        "intencion": ganadora,

        "confianza": confianza,

        "alternativas": alternativas,

        "estado": (
            "INTENCION_DETECTADA"
        )
    }