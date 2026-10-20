import re


def crear_contexto():

    return {
        "datos": {},
        "historial": [],
        "estado": "INICIAL"
    }


def agregar_dato(
    contexto,
    nombre,
    valor
):

    if not valor:
        return contexto

    contexto["datos"][nombre] = valor

    return contexto


def obtener_dato(
    contexto,
    nombre
):

    return contexto["datos"].get(
        nombre
    )


def tiene_dato(
    contexto,
    nombre
):

    valor = obtener_dato(
        contexto,
        nombre
    )

    return (
        valor is not None
        and str(valor).strip() != ""
    )


def agregar_mensaje(
    contexto,
    rol,
    mensaje
):

    contexto["historial"].append({
        "rol": rol,
        "mensaje": mensaje
    })

    return contexto


def obtener_historial(
    contexto
):

    return contexto["historial"]


def actualizar_estado(
    contexto,
    estado
):

    contexto["estado"] = estado

    return contexto


def actualizar_contexto_desde_datos(
    contexto,
    datos
):

    if not datos:
        return contexto

    for nombre, valor in datos.items():

        if valor is None:
            continue

        if str(valor).strip() == "":
            continue

        agregar_dato(
            contexto=contexto,
            nombre=nombre,
            valor=valor
        )

    return contexto