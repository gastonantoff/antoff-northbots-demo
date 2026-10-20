import json
import os
import re
import unicodedata

from motor_contexto import (
    crear_contexto,
    actualizar_contexto_desde_datos,
    agregar_mensaje,
    obtener_historial
)

from adaptador_ia import (
    generar_respuesta_ia,
    proveedor_ia_configurado,
    ProveedorIANoDisponible,
)

from motor_cerebro import (
    procesar_mensaje,
    construir_indice_intenciones,
    construir_indice_funciones,
    construir_indice_acciones,
    construir_indice_herramientas,
    construir_indice_operaciones,
)


# =========================================================
# RUNTIME UNIVERSAL DEL ASISTENTE
# =========================================================


def cargar_json(ruta):

    if not os.path.exists(ruta):
        return {}

    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as archivo:

        return json.load(archivo)


# =========================================================
# RESOLVER RUTA DEL ASISTENTE
# =========================================================


def resolver_ruta_asistente(
    archivo,
    ruta_base=None
):

    if ruta_base is None:
        ruta_base = os.path.dirname(os.path.abspath(configuracion)) if os.path.isabs(configuracion) else os.getcwd()

    if os.path.isabs(archivo):
        return archivo

    return os.path.join(
        ruta_base,
        archivo
    )


# =========================================================
# CARGAR CONFIGURACIÓN
# =========================================================


def cargar_configuracion_asistente(
    ruta_base
):

    return cargar_json(
        resolver_ruta_asistente(
            "configuracion.json",
            ruta_base
        )
    )


def cargar_cerebro_asistente(
    ruta_base
):

    return cargar_json(
        resolver_ruta_asistente(
            "cerebro.json",
            ruta_base
        )
    )


def cargar_personalidad_asistente(
    ruta_base
):

    return cargar_json(
        resolver_ruta_asistente(
            "personalidad.json",
            ruta_base
        )
    )


# =========================================================
# PREPARAR CEREBRO
# =========================================================


def preparar_cerebro(
    configuracion_cerebro
):

    if not configuracion_cerebro:
        return None

    cerebro = configuracion_cerebro.copy()

    cerebro.setdefault(
        "estado",
        "CARGADO"
    )

    # Los cerebros guardados en JSON no serializan los índices auxiliares.
    # Se reconstruyen al cargarlos para que las relaciones del asistente se
    # resuelvan igual que durante el ensamblado.
    cerebro = construir_indice_intenciones(cerebro)
    cerebro = construir_indice_funciones(cerebro)
    cerebro = construir_indice_acciones(cerebro)
    cerebro = construir_indice_herramientas(cerebro)
    cerebro = construir_indice_operaciones(cerebro)

    return cerebro


# =========================================================
# PREPARAR CONTEXTO
# =========================================================


def preparar_contexto(
    contexto=None
):

    if contexto is None:
        contexto = crear_contexto()

    return contexto


# =========================================================
# EXTRAER DATOS DE CONFIGURACIÓN
# =========================================================


def extraer_datos_configuracion(
    configuracion
):

    datos = {}

    empresa = configuracion.get(
        "empresa",
        {}
    )

    if empresa:

        nombre = empresa.get(
            "nombre"
        )

        if nombre:
            datos["empresa_nombre"] = nombre

        rubro = empresa.get(
            "rubro"
        )

        if rubro:
            datos["empresa_rubro"] = rubro

    return datos


def normalizar_texto_catalogo(texto):
    """Normaliza texto para reconocer productos sin depender de acentos."""
    texto = unicodedata.normalize("NFD", str(texto or "").lower())
    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    return re.sub(r"\s+", " ", texto).strip()


def extraer_producto_del_catalogo(mensaje, configuracion):
    """Relaciona una mención del catálogo con el requisito ``producto``.

    Las categorías y nombres provienen de la configuración del asistente,
    por lo que no fija productos de un negocio concreto en el motor.
    """
    texto = normalizar_texto_catalogo(mensaje)
    catalogo = configuracion.get("conocimiento", {}).get("catalogo", [])

    for item in catalogo:
        nombre = str(item.get("nombre", "")).strip()
        categoria = str(item.get("categoria", "")).strip()

        if not nombre:
            continue

        candidatos = [nombre, categoria]

        # "Remeras" y "remera", por ejemplo, refieren al mismo ítem.
        if categoria.lower().endswith("s"):
            candidatos.append(categoria[:-1])

        for candidato in candidatos:
            termino = normalizar_texto_catalogo(candidato)
            if len(termino) >= 3 and termino in texto:
                return {"producto": nombre}

    return {}


# =========================================================
# GENERAR RESPUESTA BASE
# =========================================================


def generar_respuesta(
    resultado_cerebro,
    personalidad
):

    if not resultado_cerebro:

        return {
            "texto": "",
            "tipo": "ERROR"
        }

    estado = resultado_cerebro.get(
        "estado"
    )

    if estado == "INTENCION_NO_DETECTADA":

        return {
            "texto": (
                "No estoy seguro de haber entendido "
                "tu solicitud. ¿Podés explicarme "
                "un poco mejor qué necesitás?"
            ),
            "tipo": "ACLARACION"
        }

    if estado == "INFORMACION_INCOMPLETA":

        decision = resultado_cerebro.get(
            "decision",
            {}
        )

        requisito = decision.get(
            "requisito"
        )

        if requisito:

            nombre = requisito.get(
                "nombre",
                requisito.get(
                    "codigo",
                    "dato necesario"
                )
            )

            return {
                "texto": (
                    f"Para poder ayudarte necesito "
                    f"que me indiques {nombre}."
                ),
                "tipo": "PEDIR_DATO"
            }

        return {
            "texto": (
                "Necesito algunos datos más "
                "para poder ayudarte."
            ),
            "tipo": "PEDIR_DATO"
        }

    if estado == "EJECUCION_BLOQUEADA":

        autonomia = resultado_cerebro.get(
            "autonomia",
            {}
        )

        autorizacion = autonomia.get(
            "autorizacion",
            {}
        )

        motivo = autorizacion.get(
            "motivo"
        )

        if motivo == "REQUIERE_CONFIRMACION":

            return {
                "texto": (
                    "Necesito tu confirmación "
                    "antes de realizar esta acción."
                ),
                "tipo": "CONFIRMACION"
            }

        return {
            "texto": (
                "La acción solicitada no puede "
                "ejecutarse automáticamente."
            ),
            "tipo": "BLOQUEADO"
        }

    if estado == "FUNCION_NO_ENCONTRADA":

        return {
            "texto": (
                "Entendí lo que necesitás, pero "
                "no tengo una función configurada "
                "para resolverlo."
            ),
            "tipo": "FUNCION_NO_DISPONIBLE"
        }

    if estado == "ACCION_NO_ENCONTRADA":

        return {
            "texto": (
                "La función está configurada, "
                "pero no tiene una acción disponible."
            ),
            "tipo": "ACCION_NO_DISPONIBLE"
        }

    if estado == "HERRAMIENTA_NO_ENCONTRADA":

        return {
            "texto": (
                "La acción está configurada, "
                "pero no encuentro la herramienta "
                "necesaria para ejecutarla."
            ),
            "tipo": "HERRAMIENTA_NO_DISPONIBLE"
        }

    if estado == "LISTO_PARA_EJECUTAR":

        intencion = resultado_cerebro.get(
            "intencion",
            {}
        )

        nombre = intencion.get(
            "nombre",
            "la solicitud"
        )

        return {
            "texto": (
                f"Entendí tu solicitud: "
                f"{nombre}. La acción está "
                f"preparada para ejecutarse."
            ),
            "tipo": "LISTO_PARA_EJECUTAR"
        }

    return {
        "texto": (
            "Procesé tu solicitud, pero "
            "no pude generar una respuesta."
        ),
        "tipo": "SIN_RESPUESTA"
    }



def construir_mensajes_ollama(
    configuracion,
    personalidad,
    contexto,
):
    asistente = configuracion.get("asistente", {})
    empresa = configuracion.get("empresa", {})
    conocimiento = configuracion.get("conocimiento", {})

    datos_empresa = {
        "nombre": empresa.get("nombre"),
        "rubro": empresa.get("rubro"),
        "catalogo": conocimiento.get("catalogo", []),
        "conocimiento_general": conocimiento.get(
            "conocimiento_general",
            []
        ),
    }

    instrucciones = personalidad.get(
        "instrucciones_sistema",
        []
    )

    if not instrucciones:
        instrucciones = personalidad.get(
            "personalidad",
            {}
        ).get("instrucciones", [])

    prompt_sistema = "\n".join(
        [
            "Respondé siempre en español claro y cordial.",
            (
                "Sos el asistente digital de: "
                f"{asistente.get('nombre', 'la empresa')}."
            ),
            (
                "Representás a la empresa: "
                f"{empresa.get('nombre', 'no informada')}."
            ),
            "Usá solamente los datos proporcionados.",
            "No inventes precios, horarios, políticas ni acciones realizadas.",
            (
                "No ejecutes acciones, pagos, reservas ni cambios: "
                "si hace falta, pedí confirmación o derivá a una persona."
            ),
            "Instrucciones de personalidad:",
            "\n".join(instrucciones),
            "Información del negocio:",
            json.dumps(
                datos_empresa,
                ensure_ascii=False
            ),
        ]
    )

    mensajes = [
        {
            "role": "system",
            "content": prompt_sistema,
        }
    ]

    historial = obtener_historial(contexto)

    for item in historial[-10:]:
        rol = item.get("rol")
        contenido = item.get("mensaje", "").strip()

        if not contenido:
            continue

        if rol == "usuario":
            rol_ollama = "user"
        elif rol == "asistente":
            rol_ollama = "assistant"
        else:
            continue

        mensajes.append(
            {
                "role": rol_ollama,
                "content": contenido,
            }
        )

    return mensajes


def generar_respuesta_con_ia(
    resultado_cerebro,
    configuracion,
    personalidad,
    contexto,
):
    respuesta_segura = generar_respuesta(
        resultado_cerebro,
        personalidad,
    )

    if not proveedor_ia_configurado(configuracion):
        return respuesta_segura

    if resultado_cerebro.get("estado") == "EJECUCION_BLOQUEADA":
        return respuesta_segura

    try:
        return generar_respuesta_ia(
            construir_mensajes_ollama(
                configuracion,
                personalidad,
                contexto,
            ),
            configuracion,
        )
    except ProveedorIANoDisponible as error:
        # El detalle queda solo en el registro del servidor. No incluye la
        # clave de API y permite diagnosticar un proveedor mal configurado.
        print(f"[IA] Respuesta de nube no disponible: {error}")
        return respuesta_segura

# =========================================================
# EJECUTAR ASISTENTE
# =========================================================


def ejecutar_asistente(
    mensaje,
    contexto=None,
    configuracion="configuracion.json",
    cerebro="cerebro.json",
    personalidad="personalidad.json"
):

    ruta_base = os.getcwd()

    configuracion_data = cargar_json(
        resolver_ruta_asistente(
            configuracion,
            ruta_base
        )
    )

    cerebro_data = cargar_json(
        resolver_ruta_asistente(
            cerebro,
            ruta_base
        )
    )

    personalidad_data = cargar_json(
        resolver_ruta_asistente(
            personalidad,
            ruta_base
        )
    )

    if not configuracion_data:

        return {
            "estado": "CONFIGURACION_NO_ENCONTRADA",
            "exito": False,
            "respuesta": {
                "texto": "No se encontró la configuración del asistente."
            }
        }

    if not cerebro_data:

        return {
            "estado": "CEREBRO_NO_ENCONTRADO",
            "exito": False,
            "respuesta": {
                "texto": "No se encontró el cerebro del asistente."
            }
        }

    cerebro_data = preparar_cerebro(cerebro_data)

    contexto = preparar_contexto(
        contexto
    )

    datos_configuracion = (
        extraer_datos_configuracion(
            configuracion_data
        )
    )

    actualizar_contexto_desde_datos(
        contexto,
        datos_configuracion
    )

    # Si la persona ya nombró un producto del catálogo, no volver a pedirle
    # ese mismo dato. Los datos explícitos cargados por otros flujos conservan
    # prioridad porque esta actualización solo completa ``producto``.
    if not contexto.get("datos", {}).get("producto"):
        actualizar_contexto_desde_datos(
            contexto,
            extraer_producto_del_catalogo(
                mensaje,
                configuracion_data,
            ),
        )

    resultado_cerebro = procesar_mensaje(
        cerebro_data,
        mensaje,
        contexto
    )

    respuesta = generar_respuesta_con_ia(
        resultado_cerebro=resultado_cerebro,
        configuracion=configuracion_data,
        personalidad=personalidad_data,
        contexto=contexto,
    )

    agregar_mensaje(
        contexto,
        "asistente",
        respuesta.get("texto", ""),
    )


    if respuesta.get("tipo") in (
        "OLLAMA_LOCAL",
        "CLOUDFLARE_WORKERS_AI",
        "GEMINI_API",
    ):
        estado_final = (
            "RESPUESTA_GENERADA_LOCALMENTE"
            if respuesta.get("tipo") == "OLLAMA_LOCAL"
            else "RESPUESTA_GENERADA_EN_NUBE"
        )
        exito_final = True
    else:
        estado_final = resultado_cerebro.get("estado")
        exito_final = resultado_cerebro.get(
            "exito",
            False,
        )

    return {
       "estado": estado_final,

        "exito": exito_final,

        "respuesta": respuesta,

        "asistente": configuracion_data.get(
            "asistente",
            {}
        ),

        "personalidad": personalidad_data,

        "resultado_cerebro": resultado_cerebro
    }
