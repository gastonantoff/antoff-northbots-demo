from motor_herramientas import (
    seleccionar_herramienta,
    ejecutar_herramienta
)


def crear_orquestacion(
    objetivo,
    pasos=None
):

    if pasos is None:
        pasos = []

    return {
        "objetivo": objetivo,
        "pasos": pasos,
        "paso_actual": 0,
        "estado": "INICIAL",
        "resultados": [],
        "errores": []
    }


def agregar_paso(
    orquestacion,
    operacion,
    datos=None
):

    if datos is None:
        datos = {}

    orquestacion["pasos"].append({
        "operacion": operacion,
        "datos": datos,
        "estado": "PENDIENTE",
        "resultado": None
    })

    return orquestacion


def obtener_paso_actual(
    orquestacion
):

    pasos = orquestacion.get(
        "pasos",
        []
    )

    indice = orquestacion.get(
        "paso_actual",
        0
    )

    if indice >= len(pasos):
        return None

    return pasos[indice]


def avanzar_paso(
    orquestacion
):

    orquestacion["paso_actual"] += 1

    return orquestacion


def objetivo_cumplido(
    orquestacion
):

    pasos = orquestacion.get(
        "pasos",
        []
    )

    if not pasos:
        return False

    return all(
        paso.get("estado")
        == "COMPLETADO"
        for paso in pasos
    )


def ejecutar_paso(
    orquestacion,
    herramientas
):

    paso = obtener_paso_actual(
        orquestacion
    )

    if paso is None:

        if objetivo_cumplido(
            orquestacion
        ):
            orquestacion["estado"] = (
                "OBJETIVO_CUMPLIDO"
            )
        else:
            orquestacion["estado"] = (
                "SIN_PASOS"
            )

        return orquestacion

    herramienta = seleccionar_herramienta(
        herramientas,
        paso["operacion"]
    )

    if not herramienta:

        paso["estado"] = "ERROR"

        paso["resultado"] = {
            "estado": "HERRAMIENTA_NO_ENCONTRADA",
            "exito": False
        }

        orquestacion["errores"].append(
            paso["resultado"]
        )

        orquestacion["estado"] = (
            "ERROR"
        )

        return orquestacion

    resultado = ejecutar_herramienta(
        herramienta,
        paso["datos"]
    )

    paso["resultado"] = resultado

    if resultado.get("exito"):

        paso["estado"] = "COMPLETADO"

        orquestacion["resultados"].append(
            resultado
        )

        avanzar_paso(
            orquestacion
        )

        if objetivo_cumplido(
            orquestacion
        ):

            orquestacion["estado"] = (
                "OBJETIVO_CUMPLIDO"
            )

        else:

            orquestacion["estado"] = (
                "CONTINUANDO"
            )

    else:

        paso["estado"] = "DETENIDO"

        orquestacion["estado"] = (
            "EJECUCION_DETENIDA"
        )

    return orquestacion


def ejecutar_orquestacion(
    orquestacion,
    herramientas,
    limite_pasos=10
):

    pasos_ejecutados = 0

    while (
        pasos_ejecutados
        < limite_pasos
    ):

        if (
            orquestacion.get("estado")
            == "OBJETIVO_CUMPLIDO"
        ):
            break

        if (
            orquestacion.get("estado")
            in [
                "ERROR",
                "EJECUCION_DETENIDA"
            ]
        ):
            break

        estado_anterior = (
            orquestacion.get(
                "estado"
            )
        )

        ejecutar_paso(
            orquestacion,
            herramientas
        )

        pasos_ejecutados += 1

        estado_actual = (
            orquestacion.get(
                "estado"
            )
        )

        if (
            estado_actual
            == estado_anterior
            and
            estado_actual
            != "CONTINUANDO"
        ):
            break

    if (
        orquestacion.get("estado")
        != "OBJETIVO_CUMPLIDO"
        and pasos_ejecutados
        >= limite_pasos
    ):

        orquestacion["estado"] = (
            "LIMITE_DE_PASOS"
        )

    return orquestacion