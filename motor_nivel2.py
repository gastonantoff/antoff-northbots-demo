from motor_intenciones import seleccionar_intencion

from motor_contexto import (
    crear_contexto,
    agregar_mensaje
)

from motor_requisitos import (
    analizar_resolucion
)

from motor_decisiones import (
    determinar_decision
)

from db_manager import (
    obtener_requisitos_intencion
)


def convertir_requisitos(
    requisitos_bd
):

    requisitos = []

    for requisito in requisitos_bd:

        requisitos.append({
            "id": requisito[0],
            "intencion_id": requisito[1],
            "codigo": requisito[2],
            "nombre": requisito[3],
            "tipo": requisito[4],
            "obligatorio": requisito[5] == 1,
            "prioridad": requisito[6],
            "descripcion": requisito[7],
            "activo": requisito[8] == 1
        })

    return requisitos


def obtener_requisitos_activos(
    intencion_id
):

    requisitos_bd = (
        obtener_requisitos_intencion(
            intencion_id
        )
    )

    requisitos = convertir_requisitos(
        requisitos_bd
    )

    requisitos_activos = [
        requisito
        for requisito in requisitos
        if requisito["activo"]
    ]

    return requisitos_activos


def procesar_nivel2(
    mensaje,
    contexto=None
):

    if contexto is None:

        contexto = crear_contexto()

    agregar_mensaje(
        contexto=contexto,
        rol="usuario",
        mensaje=mensaje
    )

    resultado_intencion = (
        seleccionar_intencion(
            mensaje
        )
    )

    if (
        resultado_intencion["estado"]
        == "INTENCION_NO_DETECTADA"
    ):

        return {
            "contexto": contexto,
            "intencion": None,
            "resolucion": None,
            "decision": determinar_decision(
                resultado_intencion,
                None
            )
        }

    intencion = resultado_intencion[
        "intencion"
    ]

    intencion_id = intencion[
        "intencion_id"
    ]

    requisitos = (
        obtener_requisitos_activos(
            intencion_id
        )
    )

    resultado_resolucion = (
        analizar_resolucion(
            intencion=intencion,
            contexto=contexto,
            requisitos=requisitos
        )
    )

    decision = determinar_decision(
        resultado_intencion,
        resultado_resolucion
    )

    return {
        "contexto": contexto,
        "intencion": intencion,
        "resolucion": resultado_resolucion,
        "decision": decision
    }