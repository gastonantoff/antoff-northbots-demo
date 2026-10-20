def determinar_decision(
    resultado_intencion,
    resultado_resolucion
):

    if not resultado_intencion:

        return {
            "tipo": "PEDIR_ACLARACION",
            "motivo": "INTENCION_NO_DETECTADA",
            "requisito": None
        }

    if resultado_intencion.get(
        "estado"
    ) == "INTENCION_NO_DETECTADA":

        return {
            "tipo": "PEDIR_ACLARACION",
            "motivo": "INTENCION_NO_DETECTADA",
            "requisito": None
        }

    if not resultado_resolucion:

        return {
            "tipo": "PEDIR_ACLARACION",
            "motivo": "SIN_RESULTADO_DE_RESOLUCION",
            "requisito": None
        }

    estado = resultado_resolucion.get(
        "estado"
    )

    if estado == "INFORMACION_INCOMPLETA":

        requisito = (
            resultado_resolucion.get(
                "siguiente_requisito"
            )
        )

        return {
            "tipo": "PEDIR_DATO",
            "motivo": "FALTA_INFORMACION",
            "requisito": requisito
        }

    if estado == "LISTO_PARA_RESOLVER":

        return {
            "tipo": "EJECUTAR_ACCION",
            "motivo": "INFORMACION_COMPLETA",
            "requisito": None
        }

    if estado == "INTENCION_NO_DETECTADA":

        return {
            "tipo": "PEDIR_ACLARACION",
            "motivo": "INTENCION_NO_DETECTADA",
            "requisito": None
        }

    return {
        "tipo": "PEDIR_ACLARACION",
        "motivo": "ESTADO_NO_RECONOCIDO",
        "requisito": None
    }