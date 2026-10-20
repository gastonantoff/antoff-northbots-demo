import os
import json
import hmac

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, PlainTextResponse, HTMLResponse, JSONResponse 
from conector_demo_local import (
    responder_demo,
    responder_asistente_local,
)
from db_manager import (

    #Base de datos
    crear_base,

    #Negocios
    guardar_negocio,
    obtener_negocios,
    obtener_negocio_por_id,
    actualizar_negocio,
    eliminar_negocio,

    #Proyectos
    guardar_proyecto,
    obtener_proyectos,
    obtener_proyecto_por_id,

    #Empresa
    guardar_empresa_proyecto,
    
    #Perfil de negocio
    guardar_perfil_negocio,
    obtener_perfil_negocio,

    #Catalogo
    agregar_producto_servicio,
    obtener_productos_servicios,
    obtener_items_catalogo,
    obtener_producto_servicio_por_id,
    actualizar_producto_servicio,
    eliminar_producto_servicio,

    guardar_item_catalogo,
    actualizar_item_catalogo,
    eliminar_item_catalogo,
    obtener_item_catalogo_por_id,

    #Conocimiento
    guardar_conocimiento,
    obtener_conocimiento,
    obtener_conocimiento_por_id,

    #Personalidad
    guardar_personalidad,
    obtener_personalidad,

    #Capacidad
    guardar_capacidades,
    obtener_capacidades,

    #IA
    guardar_configuracion_ia,
    obtener_configuracion_ia,

    #Canales
    guardar_canales,
    obtener_canales,

    #Asistente
    generar_asistente as generar_asistente_legacy,
    obtener_asistente,

    #Accesos y permisos
    guardar_acceso,
    obtener_accesos,
    actualizar_acceso,
    cambiar_estado_acceso,

    #Flujos y reglas
    guardar_flujo,
    obtener_flujos,
    actualizar_flujo,
    cambiar_estado_flujo,

    #Biblioteca de funciones
    guardar_funcion,
    obtener_funciones,
    obtener_funcion,
    actualizar_funcion,
    cambiar_estado_funcion,

    #Estación 12 — Intenciones
    crear_intencion,
    obtener_intenciones,
    obtener_intencion,
    actualizar_intencion,
    eliminar_intencion,

    #Funciones asignadas a proyectos
    asignar_funcion_proyecto,
    obtener_funciones_proyecto,
    obtener_funciones_disponibles_para_proyecto,
    cambiar_estado_funcion_proyecto,
    quitar_funcion_proyecto,

    #Pantalla herramientas
    guardar_herramienta_proyecto,
    obtener_herramientas_proyecto,
    obtener_herramienta_por_id,
    cambiar_estado_herramienta,
    eliminar_herramienta_proyecto,

    #interfaz
    guardar_accion_herramienta,
    obtener_acciones_herramienta,
    obtener_accion_por_id,
    cambiar_estado_accion,
    eliminar_accion_herramienta,

    #Funciones asignadas
    asignar_accion_a_funcion,
    obtener_acciones_de_funcion,
    obtener_acciones_disponibles_para_funcion,
    cambiar_estado_accion_funcion,
    quitar_accion_de_funcion,

    obtener_capacidades_funcion,
    obtener_capacidades_proyecto,

    #Estación 12 — Intenciones
    crear_intencion,
    obtener_intenciones,
    obtener_intencion,
    actualizar_intencion,
    eliminar_intencion,

    #Estación 12 — Intenciones del proyecto
    agregar_intencion_proyecto,
    obtener_intenciones_proyecto,
    obtener_intenciones_disponibles,
    cambiar_estado_intencion_proyecto,
    actualizar_prioridad_intencion_proyecto,
    quitar_intencion_proyecto,

    # Estación 12 — Patrones de intención
    crear_patron_intencion,
    obtener_patrones_intencion,
    obtener_patron_intencion,
    actualizar_patron_intencion,
    eliminar_patron_intencion,

)

from conector_instagram import (
    obtener_estado_conector,
    procesar_evento_instagram,
    verificar_firma_evento,
    verificar_token_webhook,
    enviar_mensaje_instagram,
    extraer_mensajes_instagram,
    responder_con_asistente_instagram,
    
)

app = FastAPI()

crear_base()

@app.get("/integraciones/demo/estado")
def estado_demo_local():
    secreto = os.getenv(
        "MANYCHAT_DEMO_SECRET",
        ""
    ).strip()

    return JSONResponse(
        content={
            "asistente": "DEMO-ANTOFF",
            "estado": (
                "LISTO_PARA_CONECTAR"
                if secreto
                else "CONFIGURACION_PENDIENTE"
            ),
            "requiere_secreto": not bool(secreto),
        }
    )


@app.post("/integraciones/demo/responder")
async def responder_demo_desde_canal(request: Request):
    secreto_esperado = os.getenv(
        "MANYCHAT_DEMO_SECRET",
        ""
    ).strip()

    if not secreto_esperado:
        raise HTTPException(
            status_code=503,
            detail=(
                "Falta configurar MANYCHAT_DEMO_SECRET."
            ),
        )

    secreto_recibido = request.headers.get(
        "x-antoff-secret",
        ""
    ).strip()

    if not hmac.compare_digest(
        secreto_recibido,
        secreto_esperado,
    ):
        raise HTTPException(
            status_code=401,
            detail="No autorizado.",
        )

    try:
        datos = await request.json()
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="El cuerpo debe ser JSON válido.",
        ) from error

    texto = (
        datos.get("mensaje")
        or datos.get("message")
        or datos.get("text")
        or ""
    )

    conversacion_id = (
        datos.get("conversacion_id")
        or datos.get("subscriber_id")
        or datos.get("user_id")
        or "demo_local"
    )

    resultado = responder_demo(
        conversacion_id,
        texto,
    )

    return JSONResponse(content=resultado)
        
@app.get("/integraciones/instagram/estado")
def estado_integracion_instagram():
    """Muestra el estado sin revelar secretos."""
    return JSONResponse(content=obtener_estado_conector())


@app.get("/webhooks/instagram")
async def verificar_webhook_instagram(request: Request):
    """Responde al desafío inicial de verificación de Meta."""
    parametros = request.query_params
    modo = parametros.get("hub.mode")
    token = parametros.get("hub.verify_token")
    desafio = parametros.get("hub.challenge")

    if modo == "subscribe" and verificar_token_webhook(token):
        return PlainTextResponse(desafio or "")

    raise HTTPException(
        status_code=403,
        detail="No se pudo verificar el webhook de Instagram.",
    )


@app.post("/webhooks/instagram")
async def recibir_evento_instagram(request: Request):
    """Recibe eventos firmados por Meta sin responder mensajes aún."""
    cuerpo = await request.body()
    firma = request.headers.get("x-hub-signature-256")

    if not verificar_firma_evento(cuerpo, firma):
        raise HTTPException(
            status_code=403,
            detail="Firma de Instagram no válida.",
        )

    try:
        evento = json.loads(cuerpo)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="El evento de Instagram no contiene JSON válido.",
        ) from error

    resultado = procesar_evento_instagram(evento)

    if not resultado["aceptado"]:
        raise HTTPException(status_code=422, detail=resultado)

    mensajes = extraer_mensajes_instagram(evento)
    respuestas = []

    for mensaje in mensajes:
        texto_respuesta = responder_con_asistente_instagram(
            mensaje["remitente_id"],
            mensaje["texto"],
        )

        envio = enviar_mensaje_instagram(
            mensaje["remitente_id"],
            texto_respuesta,
        )

        respuestas.append({
            "enviado": envio["enviado"],
        })

    return JSONResponse(
        content={
            "estado": "EVENTO_RECIBIDO",
            "mensajes_procesados": len(mensajes),
            "respuestas": respuestas,
        }
    )

import os

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

@app.get("/demo")
def ver_demo_chat(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="demo_chat.html",
        context={
            "titulo_demo": "ANT0FF Northbots · Demo local",
            "subtitulo_demo": "Asistente digital para negocios",
            "saludo_demo": (
                "¡Hola! Soy el asistente digital de ANT0FF Northbots. "
                "Contame sobre tu negocio y qué te gustaría automatizar."
            ),
            "endpoint_chat": "/demo/chat",
            "clave_conversacion": "antoff_demo_conversacion",
        },
    )


@app.post("/demo/chat")
async def conversar_con_demo(request: Request):
    cliente = request.client.host if request.client else ""

    if cliente not in {"127.0.0.1", "::1"}:
        raise HTTPException(
            status_code=403,
            detail="La demo local solo acepta conexiones locales.",
        )

    try:
        datos = await request.json()
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="El cuerpo debe ser JSON válido.",
        ) from error

    if not isinstance(datos, dict):
        raise HTTPException(
            status_code=422,
            detail="El cuerpo debe ser un objeto JSON.",
        )

    resultado = responder_demo(
        datos.get("conversacion_id"),
        datos.get("mensaje", ""),
    )

    return JSONResponse(content=resultado)


@app.get("/demo/lumen-moda")
def ver_demo_lumen_moda(request: Request):
    """Prueba local del asistente ficticio generado para Lumen Moda."""
    return templates.TemplateResponse(
        request=request,
        name="demo_chat.html",
        context={
            "titulo_demo": "Lumen Moda · Demo local",
            "subtitulo_demo": "Asistente comercial ficticio de prueba",
            "saludo_demo": (
                "¡Hola! Soy Lumi, la asesora digital de Lumen Moda. "
                "Podés consultarme por productos, precios, talles o envíos."
            ),
            "endpoint_chat": "/demo/lumen-moda/chat",
            "clave_conversacion": "lumen_moda_demo_conversacion",
        },
    )


@app.post("/demo/lumen-moda/chat")
async def conversar_con_lumen_moda(request: Request):
    cliente = request.client.host if request.client else ""

    if cliente not in {"127.0.0.1", "::1"}:
        raise HTTPException(
            status_code=403,
            detail="La demo local solo acepta conexiones locales.",
        )

    try:
        datos = await request.json()
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="El cuerpo debe ser JSON válido.",
        ) from error

    if not isinstance(datos, dict):
        raise HTTPException(
            status_code=422,
            detail="El cuerpo debe ser un objeto JSON.",
        )

    resultado = responder_asistente_local(
        "AST-000002",
        datos.get("conversacion_id"),
        datos.get("mensaje", ""),
    )

    return JSONResponse(content=resultado)

@app.get("/")
def inicio():
    return {"mensaje": "PRUEBA UNICA 987654"}


@app.get("/negocios")
def listar_negocios(request: Request):
    negocios = obtener_negocios()

    return templates.TemplateResponse(
        request=request,
        name="negocios.html",
        context={"negocios": negocios}
    )


@app.get("/proyectos")
def proyectos(request: Request):
    proyectos = obtener_proyectos()

    return templates.TemplateResponse(
        request=request,
        name="proyectos.html",
        context={
            "proyectos": proyectos
        }
    )


@app.get("/proyectos/nuevo")
def nuevo_proyecto(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="nuevo_proyecto.html",
        context={}
    )


@app.get("/editar/{id}")
def editar_negocio(id: int, request: Request):
    negocio = obtener_negocio_por_id(id)

    return templates.TemplateResponse(
        request=request,
        name="editar_negocio.html",
        context={"negocio": negocio}
    )


@app.post("/productos/{negocio_id}/actualizar/{producto_id}")
def actualizar_producto(
    negocio_id: int,
    producto_id: int,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    precio: float = Form(...),
    tipo: str = Form(...)
):
    actualizar_producto_servicio(
        producto_id,
        nombre,
        descripcion,
        precio,
        tipo
    )

    return RedirectResponse(
        url=f"/productos/{negocio_id}",
        status_code=303
    )


@app.post("/actualizar/{id}")
def actualizar(
    id: int,
    nombre: str = Form(...),
    rubro: str = Form(...),
    whatsapp: str = Form(...),
    horario: str = Form(...),
    direccion: str = Form(...)
):
    actualizar_negocio(
        id,
        nombre,
        rubro,
        whatsapp,
        horario,
        direccion
    )

    return RedirectResponse(
    url="/negocios",
    status_code=303
)


@app.get("/eliminar/{id}")
def eliminar(id: int):
    eliminar_negocio(id)

    return RedirectResponse(
    url="/negocios",
    status_code=303
)


@app.get("/productos/{negocio_id}/editar/{producto_id}")
def editar_producto(
    request: Request,
    negocio_id: int,
    producto_id: int
):
    negocio = obtener_negocio_por_id(negocio_id)
    producto = obtener_producto_servicio_por_id(producto_id)

    if negocio is None or producto is None:
        raise HTTPException(status_code=404, detail="No encontrado")

    return templates.TemplateResponse(
        request=request,
        name="editar_producto.html",
        context={
            "negocio": negocio,
            "producto": producto
        }
    )


@app.get("/perfil/{id}")
def perfil_negocio(id: int, request: Request):
    negocio = obtener_negocio_por_id(id)
    perfil = obtener_perfil_negocio(id)

    return templates.TemplateResponse(
        request=request,
        name="perfil_negocio.html",
        context={
            "negocio": negocio,
            "perfil": perfil
        }
    )


@app.get("/productos/{id}")
def productos(request: Request, id: int):
    negocio = obtener_negocio_por_id(id)

    if negocio is None:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    productos = obtener_productos_servicios(id)

    return templates.TemplateResponse(
        request=request,
        name="productos_servicios.html",
        context={
            "negocio": negocio,
            "productos": productos
        }
    )


@app.post("/productos/{id}/agregar")
def agregar_producto(
    id: int,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    precio: float = Form(...),
    tipo: str = Form(...)
):
    agregar_producto_servicio(
        id,
        nombre,
        descripcion,
        precio,
        tipo
    )

    return RedirectResponse(
        url=f"/productos/{id}",
        status_code=303
    )


@app.post("/proyectos/guardar")
def guardar_nuevo_proyecto(
    nombre: str = Form(...),
    cliente: str = Form(...),
    empresa: str = Form(...),
    rubro: str = Form(...),
    estado: str = Form(...)
):
    guardar_proyecto(
        nombre,
        cliente,
        empresa,
        rubro,
        estado
    )

    return RedirectResponse(
        url="/proyectos",
        status_code=303
    )

@app.get("/productos/{negocio_id}/eliminar/{producto_id}")
def eliminar_producto(negocio_id: int, producto_id: int):
    eliminar_producto_servicio(producto_id)

    return RedirectResponse(
        url=f"/productos/{negocio_id}",
        status_code=303
    )

@app.post("/perfil/{id}/guardar")
def guardar_perfil(
    id: int,
    descripcion: str = Form(""),
    productos_servicios: str = Form(""),
    formas_pago: str = Form(""),
    entregas_reservas: str = Form(""),
    informacion_adicional: str = Form("")
):
    guardar_perfil_negocio(
        id,
        descripcion,
        productos_servicios,
        formas_pago,
        entregas_reservas,
        informacion_adicional
    )

    return RedirectResponse(
        url=f"/perfil/{id}",
        status_code=303
    )



@app.post("/guardar")
def guardar(
    nombre: str = Form(...),
    rubro: str = Form(...),
    whatsapp: str = Form(...),
    horario: str = Form(...),
    direccion: str = Form(...)
):
    guardar_negocio(
        nombre,
        rubro,
        whatsapp,
        horario,
        direccion
    )

    return RedirectResponse(
    url="/negocios",
    status_code=303
)


@app.get("/proyectos/{id}")
def ver_proyecto(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="proyecto.html",
        context={
            "proyecto": proyecto
        }
    )


@app.get("/proyectos/{id}/empresa")
def empresa_proyecto(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="empresa.html",
        context={
            "proyecto": proyecto
        }
    )


@app.post("/proyectos/{id}/empresa/guardar")
def guardar_empresa(
    id: int,
    nombre: str = Form(""),
    rubro: str = Form(""),
    whatsapp: str = Form(""),
    direccion: str = Form(""),
    horario: str = Form(""),
    sitio_web: str = Form(""),
    observaciones: str = Form("")
):
    guardar_empresa_proyecto(
        id,
        nombre,
        rubro,
        whatsapp,
        direccion,
        horario,
        sitio_web,
        observaciones
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/empresa",
        status_code=303
    )


@app.get("/proyectos/{id}/catalogo")
def catalogo_proyecto(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    items = obtener_items_catalogo(id)

    return templates.TemplateResponse(
        request=request,
        name="catalogo.html",
        context={
            "proyecto": proyecto,
            "items": items
        }
    )


@app.post("/proyectos/{id}/catalogo/guardar")
def guardar_catalogo(
    id: int,
    tipo: str = Form(...),
    categoria: str = Form(""),
    nombre: str = Form(...),
    descripcion: str = Form(""),
    precio: float = Form(0),
    observaciones: str = Form("")
):
    guardar_item_catalogo(
        id,
        tipo,
        categoria,
        nombre,
        descripcion,
        precio,
        observaciones
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/catalogo",
        status_code=303
    )


@app.get("/catalogo/{id}/editar")
def editar_item_catalogo(
    request: Request,
    id: int
):
    item = obtener_item_catalogo_por_id(id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Elemento no encontrado"
        )

    return templates.TemplateResponse(
    request=request,
    name="editar_catalogo.html",
    context={
        "item": item
    }
)


@app.post("/catalogo/{id}/actualizar")
def actualizar_catalogo(
    id: int,
    tipo: str = Form(...),
    categoria: str = Form(""),
    nombre: str = Form(...),
    descripcion: str = Form(""),
    precio: float = Form(0),
    observaciones: str = Form("")
):
    item = obtener_item_catalogo_por_id(id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Elemento no encontrado"
        )

    actualizar_item_catalogo(
        id,
        tipo,
        categoria,
        nombre,
        descripcion,
        precio,
        observaciones
    )

    return RedirectResponse(
        url=f"/proyectos/{item[1]}/catalogo",
        status_code=303
    )    


@app.get("/catalogo/{id}/eliminar")
def eliminar_catalogo(id: int):
    item = obtener_item_catalogo_por_id(id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Elemento no encontrado"
        )

    proyecto_id = item[1]

    eliminar_item_catalogo(id)

    return RedirectResponse(
        url=f"/proyectos/{proyecto_id}/catalogo",
        status_code=303
    )


@app.get("/proyectos/{id}/conocimiento")
def conocimiento_proyecto(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    conocimientos = obtener_conocimiento(id)

    return templates.TemplateResponse(
        request=request,
        name="conocimiento.html",
        context={
            "proyecto": proyecto,
            "conocimientos": conocimientos
        }
    )


@app.get("/proyectos/{id}/conocimiento/nuevo")
def nuevo_conocimiento(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="nuevo_conocimiento.html",
        context={
            "proyecto": proyecto
        }
    )


@app.post("/proyectos/{id}/conocimiento")
def guardar_conocimiento_proyecto(
    id: int,
    categoria: str = Form(...),
    titulo: str = Form(...),
    contenido: str = Form(...),
    observaciones: str = Form("")
):

    guardar_conocimiento(
        id,
        categoria,
        titulo,
        contenido,
        observaciones
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/conocimiento",
        status_code=303
    )


@app.get("/conocimiento/{id}/editar")
def editar_conocimiento(
    request: Request,
    id: int
):
    conocimiento = obtener_conocimiento_por_id(id)

    if conocimiento is None:
        raise HTTPException(
            status_code=404,
            detail="Conocimiento no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="editar_conocimiento.html",
        context={
            "conocimiento": conocimiento
        }
    )


@app.get("/proyectos/{id}/personalidad")
def personalidad(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    personalidad = obtener_personalidad(id)

    return templates.TemplateResponse(
    request=request,
    name="personalidad.html",
    context={
        "proyecto": proyecto,
        "personalidad": personalidad
    }
)


@app.post("/proyectos/{id}/personalidad/guardar")
def guardar_personalidad_proyecto(
    id: int,
    nombre: str = Form(""),
    rol: str = Form(""),
    objetivo: str = Form(""),
    comunicacion: str = Form(""),
    iniciativa: str = Form(""),
    longitud_respuestas: str = Form(""),
    emojis: str = Form(""),
    restricciones: str = Form(""),
    despedida: str = Form("")
):

    guardar_personalidad(
        id,
        nombre,
        rol,
        objetivo,
        comunicacion,
        iniciativa,
        longitud_respuestas,
        emojis,
        restricciones,
        despedida
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/personalidad",
        status_code=303
    )


@app.get("/proyectos/{id}/capacidades")
def capacidades(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)
    capacidades = obtener_capacidades(id)
    print("CAPACIDADES:", capacidades)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="capacidades.html",
        context={
            "proyecto": proyecto,
            "capacidades": capacidades
        }
    )


@app.post("/proyectos/{id}/capacidades/guardar")
def guardar_capacidades_proyecto(

    id: int,

    faq: str = Form(None),
    catalogo: str = Form(None),
    conocimiento: str = Form(None),
    recomendar: str = Form(None),
    turnos: str = Form(None),
    pedidos: str = Form(None),
    presupuestos: str = Form(None),
    documentacion: str = Form(None),
    clientes: str = Form(None),
    humano: str = Form(None)

):
    print("entro al post")
    
    capacidades = []

    if faq:
        capacidades.append("faq")

    if catalogo:
        capacidades.append("catalogo")

    if conocimiento:
        capacidades.append("conocimiento")

    if recomendar:
        capacidades.append("recomendar")

    if turnos:
        capacidades.append("turnos")

    if pedidos:
        capacidades.append("pedidos")

    if presupuestos:
        capacidades.append("presupuestos")

    if documentacion:
        capacidades.append("documentacion")

    if clientes:
        capacidades.append("clientes")

    if humano:
        capacidades.append("humano")

    guardar_capacidades(
        id,
        capacidades
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/capacidades",
        status_code=303
    )


@app.get("/proyectos/{id}/configuracion-ia")
def configuracion_ia(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)
    configuracion = obtener_configuracion_ia(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    if configuracion is None:
        configuracion = (
            None,
            id,
            "GPT-5.5 Mini",
            "Medio",
            "Equilibrada",
            "Medias",
            "Hace preguntas cuando es necesario",
            "Decide dentro de reglas",
            "Precisión",
            "Ninguna"
        )

    return templates.TemplateResponse(
        request=request,
        name="configuracion_ia.html",
        context={
            "proyecto": proyecto,
            "configuracion": configuracion
        }
    )

@app.post("/proyectos/{id}/configuracion-ia/guardar")
def guardar_configuracion_ia_post(
    request: Request,
    id: int,
    modelo: str = Form(...),
    razonamiento: str = Form(...),
    creatividad: str = Form(...),
    longitud: str = Form(...),
    iniciativa: str = Form(...),
    autonomia: str = Form(...),
    prioridad: str = Form(...),
    memoria: str = Form(...)
):

    guardar_configuracion_ia(
        id,
        modelo,
        razonamiento,
        creatividad,
        longitud,
        iniciativa,
        autonomia,
        prioridad,
        memoria
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/configuracion-ia",
        status_code=303
    )


@app.get("/proyectos/{id}/canales")
def canales(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)
    canales = obtener_canales(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="canales.html",
        context={
            "proyecto": proyecto,
            "canales": canales
        }
    )


@app.post("/proyectos/{id}/canales/guardar")
async def guardar_canales_proyecto(
    request: Request,
    id: int
):
    formulario = await request.form()

    canales = formulario.getlist("canal")

    guardar_canales(
        id,
        canales
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/canales",
        status_code=303
    )


@app.post("/proyectos/{id}/asistente/generar")
def generar_asistente_proyecto(id: int):
    from motor_estacion13 import fabricar_asistente

    resultado = fabricar_asistente(id)

    if not resultado.get("exito"):
        raise HTTPException(
            status_code=422,
            detail=resultado
        )

    return RedirectResponse(
        url=f"/proyectos/{id}/asistente",
        status_code=303
    )


@app.post("/proyectos/{id}/asistente/fabricar")
def fabricar_asistente_proyecto(id: int):
    from motor_estacion13 import fabricar_asistente
    resultado = fabricar_asistente(id)
    return JSONResponse(content=resultado, status_code=200 if resultado.get("exito") else 422)


@app.post("/proyectos/{id}/asistente/ejecutar-flujo")
async def ejecutar_flujo_asistente_proyecto(
    request: Request,
    id: int,
):
    """
    Ejecuta una única pasada del flujo completo:
    Estación 13 → Estación 14 → Estación 15.

    El cuerpo JSON es opcional y puede incluir:
    {
        "canales": ["web"],
        "configuraciones": {
            "web": {"url": "...", "credenciales": {...}}
        }
    }

    La conexión de 15.3 permanece como contrato lógico: este
    endpoint no realiza llamadas a proveedores externos.
    """
    if obtener_proyecto_por_id(id) is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado",
        )

    try:
        datos = await request.json()
    except Exception:
        datos = {}

    if not isinstance(datos, dict):
        raise HTTPException(
            status_code=422,
            detail="El cuerpo debe ser un objeto JSON.",
        )

    canales_solicitados = datos.get("canales")
    configuraciones = datos.get("configuraciones")

    if canales_solicitados is not None and not isinstance(
        canales_solicitados,
        list,
    ):
        raise HTTPException(
            status_code=422,
            detail="'canales' debe ser una lista.",
        )

    if configuraciones is not None and not isinstance(
        configuraciones,
        dict,
    ):
        raise HTTPException(
            status_code=422,
            detail="'configuraciones' debe ser un objeto.",
        )

    from motor_estacion13 import fabricar_asistente
    from motor_estacion14 import ejecutar_estacion14
    from motor_estacion15 import ejecutar_estacion15

    resultado_13 = fabricar_asistente(id)

    respuesta = {
        "proyecto_id": id,
        "estacion13": resultado_13,
        "estacion14": None,
        "estacion15": None,
    }

    if not resultado_13.get("exito"):
        respuesta["estado"] = "ERROR_ESTACION_13"
        return JSONResponse(content=respuesta, status_code=422)

    resultado_14 = ejecutar_estacion14(id)
    respuesta["estacion14"] = resultado_14

    if resultado_14.get("estado") != "APROBADO":
        respuesta["estado"] = "BLOQUEADO_ESTACION_14"
        return JSONResponse(content=respuesta, status_code=422)

    resultado_15 = ejecutar_estacion15(
        proyecto_id=id,
        resultado_estacion14=resultado_14,
        canales_solicitados=canales_solicitados,
        configuraciones=configuraciones,
    )
    respuesta["estacion15"] = resultado_15
    respuesta["estado"] = resultado_15.get("estado")

    return JSONResponse(
        content=respuesta,
        status_code=200 if resultado_15.get("exito") else 422,
    )


@app.get("/proyectos/{id}/asistente")
def asistente_generado(
    request: Request,
    id: int
):

    proyecto = obtener_proyecto_por_id(id)
    asistente = obtener_asistente(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="asistente.html",
        context={
            "proyecto": proyecto,
            "asistente": asistente
        }
    )


@app.get("/proyectos/{id}/accesos")
def accesos_proyecto(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)
    accesos = obtener_accesos(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="accesos.html",
        context={
            "proyecto": proyecto,
            "accesos": accesos
        }
    )


@app.post("/proyectos/{id}/accesos/guardar")
async def guardar_acceso_proyecto(
    request: Request,
    id: int
):
    formulario = await request.form()

    nombre_recurso = formulario.get("nombre_recurso")
    tipo_recurso = formulario.get("tipo_recurso")
    ubicacion = formulario.get("ubicacion")
    permiso = formulario.get("permiso")
    descripcion = formulario.get("descripcion")

    guardar_acceso(
        proyecto_id=id,
        nombre_recurso=nombre_recurso,
        tipo_recurso=tipo_recurso,
        ubicacion=ubicacion,
        permiso=permiso,
        descripcion=descripcion
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/accesos",
        status_code=303
    )


@app.post("/proyectos/{id}/accesos/{acceso_id}/actualizar")
async def actualizar_acceso_proyecto(
    request: Request,
    id: int,
    acceso_id: int
):
    formulario = await request.form()

    nombre_recurso = formulario.get("nombre_recurso")
    tipo_recurso = formulario.get("tipo_recurso")
    ubicacion = formulario.get("ubicacion")
    permiso = formulario.get("permiso")
    descripcion = formulario.get("descripcion")

    actualizar_acceso(
        acceso_id=acceso_id,
        nombre_recurso=nombre_recurso,
        tipo_recurso=tipo_recurso,
        ubicacion=ubicacion,
        permiso=permiso,
        descripcion=descripcion
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/accesos",
        status_code=303
    )


@app.post("/proyectos/{id}/accesos/{acceso_id}/estado")
async def cambiar_estado_acceso_proyecto(
    request: Request,
    id: int,
    acceso_id: int
):
    formulario = await request.form()

    activo = int(formulario.get("activo"))

    cambiar_estado_acceso(
        acceso_id=acceso_id,
        activo=activo
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/accesos",
        status_code=303
    )


@app.get("/proyectos/{id}/flujos")
def flujos_proyecto(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)
    flujos = obtener_flujos(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    return templates.TemplateResponse(
        request=request,
        name="flujos.html",
        context={
            "proyecto": proyecto,
            "flujos": flujos
        }
    )


@app.post("/proyectos/{id}/flujos/guardar")
async def guardar_flujo_proyecto(
    request: Request,
    id: int
):
    formulario = await request.form()

    nombre = formulario.get("nombre")
    descripcion = formulario.get("descripcion")
    disparador = formulario.get("disparador")
    condicion = formulario.get("condicion")
    accion = formulario.get("accion")

    prioridad = int(
        formulario.get("prioridad") or 0
    )

    guardar_flujo(
        proyecto_id=id,
        nombre=nombre,
        descripcion=descripcion,
        disparador=disparador,
        condicion=condicion,
        accion=accion,
        prioridad=prioridad
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/flujos",
        status_code=303
    )


@app.post("/proyectos/{id}/flujos/{flujo_id}/actualizar")
async def actualizar_flujo_proyecto(
    request: Request,
    id: int,
    flujo_id: int
):
    formulario = await request.form()

    nombre = formulario.get("nombre")
    descripcion = formulario.get("descripcion")
    disparador = formulario.get("disparador")
    condicion = formulario.get("condicion")
    accion = formulario.get("accion")

    prioridad = int(
        formulario.get("prioridad") or 0
    )

    actualizar_flujo(
        flujo_id=flujo_id,
        nombre=nombre,
        descripcion=descripcion,
        disparador=disparador,
        condicion=condicion,
        accion=accion,
        prioridad=prioridad
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/flujos",
        status_code=303
    )


@app.post("/proyectos/{id}/flujos/{flujo_id}/estado")
async def cambiar_estado_flujo_proyecto(
    request: Request,
    id: int,
    flujo_id: int
):
    formulario = await request.form()

    activo = int(
        formulario.get("activo")
    )

    cambiar_estado_flujo(
        flujo_id=flujo_id,
        activo=activo
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/flujos",
        status_code=303
    )


@app.get("/funciones")
def biblioteca_funciones(
    request: Request
):
    funciones = obtener_funciones()

    return templates.TemplateResponse(
        request=request,
        name="funciones.html",
        context={
            "funciones": funciones
        }
    )


@app.post("/funciones/guardar")
async def guardar_funcion_biblioteca(
    request: Request
):
    formulario = await request.form()

    nombre = formulario.get("nombre")
    categoria = formulario.get("categoria")
    descripcion = formulario.get("descripcion")
    objetivo = formulario.get("objetivo")
    estrategia_resolucion = formulario.get(
        "estrategia_resolucion"
    )

    derivacion_humana = (
        formulario.get("derivacion_humana") == "1"
    )

    guardar_funcion(
        nombre=nombre,
        categoria=categoria,
        descripcion=descripcion,
        objetivo=objetivo,
        estrategia_resolucion=estrategia_resolucion,
        derivacion_humana=derivacion_humana,
        activa=True
    )

    return RedirectResponse(
        url="/funciones",
        status_code=303
    )


@app.post("/funciones/{funcion_id}/estado")
async def cambiar_estado_funcion_biblioteca(
    request: Request,
    funcion_id: int
):
    formulario = await request.form()

    activa = formulario.get("activa") == "1"

    cambiar_estado_funcion(
        funcion_id=funcion_id,
        activa=activa
    )

    return RedirectResponse(
        url="/funciones",
        status_code=303
    )


@app.post("/funciones/{funcion_id}/actualizar")
async def actualizar_funcion_biblioteca(
    request: Request,
    funcion_id: int
):
    formulario = await request.form()

    nombre = formulario.get("nombre")
    categoria = formulario.get("categoria")
    descripcion = formulario.get("descripcion")
    objetivo = formulario.get("objetivo")
    estrategia_resolucion = formulario.get(
        "estrategia_resolucion"
    )

    derivacion_humana = (
        formulario.get("derivacion_humana") == "1"
    )

    activa = (
        formulario.get("activa") == "1"
    )

    actualizar_funcion(
        funcion_id=funcion_id,
        nombre=nombre,
        categoria=categoria,
        descripcion=descripcion,
        objetivo=objetivo,
        estrategia_resolucion=estrategia_resolucion,
        derivacion_humana=derivacion_humana,
        activa=activa
    )

    return RedirectResponse(
        url="/funciones",
        status_code=303
    )


# =========================================================
# ESTACIÓN 12 — NIVEL 1
# CATÁLOGO DE INTENCIONES
# =========================================================


@app.get("/intenciones")
def biblioteca_intenciones(
    request: Request
):
    intenciones = obtener_intenciones()

    return templates.TemplateResponse(
        request=request,
        name="intenciones.html",
        context={
            "intenciones": intenciones
        }
    )


@app.post("/intenciones/guardar")
async def guardar_intencion_biblioteca(
    request: Request
):
    formulario = await request.form()

    nombre = formulario.get("nombre")
    codigo = formulario.get("codigo")
    descripcion = formulario.get("descripcion")
    categoria = formulario.get("categoria")

    prioridad = int(
        formulario.get("prioridad") or 0
    )

    requiere_contexto = (
        formulario.get("requiere_contexto") == "1"
    )

    permite_derivacion = (
        formulario.get("permite_derivacion") == "1"
    )

    crear_intencion(
        nombre=nombre,
        codigo=codigo,
        descripcion=descripcion,
        categoria=categoria,
        prioridad=prioridad,
        requiere_contexto=requiere_contexto,
        permite_derivacion=permite_derivacion,
        activa=True
    )

    return RedirectResponse(
        url="/intenciones",
        status_code=303
    )


@app.post("/intenciones/{intencion_id}/actualizar")
async def actualizar_intencion_biblioteca(
    request: Request,
    intencion_id: int
):
    formulario = await request.form()

    nombre = formulario.get("nombre")
    codigo = formulario.get("codigo")
    descripcion = formulario.get("descripcion")
    categoria = formulario.get("categoria")

    prioridad = int(
        formulario.get("prioridad") or 0
    )

    requiere_contexto = (
        formulario.get("requiere_contexto") == "1"
    )

    permite_derivacion = (
        formulario.get("permite_derivacion") == "1"
    )

    activa = (
        formulario.get("activa") == "1"
    )

    actualizar_intencion(
        intencion_id=intencion_id,
        nombre=nombre,
        codigo=codigo,
        descripcion=descripcion,
        categoria=categoria,
        prioridad=prioridad,
        requiere_contexto=requiere_contexto,
        permite_derivacion=permite_derivacion,
        activa=activa
    )

    return RedirectResponse(
        url="/intenciones",
        status_code=303
    )


@app.post("/intenciones/{intencion_id}/eliminar")
def eliminar_intencion_biblioteca(
    intencion_id: int
):
    eliminar_intencion(
        intencion_id
    )

    return RedirectResponse(
        url="/intenciones",
        status_code=303
    )


@app.get("/proyectos/{id}/funciones")
def funciones_del_proyecto(
    request: Request,
    id: int
):
    proyecto = obtener_proyecto_por_id(id)

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    funciones_proyecto = obtener_funciones_proyecto(id)

    funciones_disponibles = (
        obtener_funciones_disponibles_para_proyecto(id)
    )

    return templates.TemplateResponse(
        request=request,
        name="funciones_proyecto.html",
        context={
            "proyecto": proyecto,
            "funciones_proyecto": funciones_proyecto,
            "funciones_disponibles": funciones_disponibles
        }
    )


@app.get("/proyectos/{proyecto_id}/herramientas")
def ver_herramientas_proyecto(
    request: Request,
    proyecto_id: int
):
    proyecto = obtener_proyecto_por_id(proyecto_id)

    if not proyecto:
        return RedirectResponse(
            url="/proyectos",
            status_code=303
        )

    herramientas = obtener_herramientas_proyecto(proyecto_id)

    return templates.TemplateResponse(
        request=request,
        name="herramientas_proyecto.html",
        context={
            "proyecto": proyecto,
            "herramientas": herramientas
        }
    )


@app.post("/proyectos/{proyecto_id}/herramientas/guardar")
def guardar_herramienta(
    proyecto_id: int,
    nombre: str = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(""),
    configuracion: str = Form("")
):
    guardar_herramienta_proyecto(
        proyecto_id,
        nombre,
        tipo,
        descripcion,
        configuracion
    )

    return RedirectResponse(
        url=f"/proyectos/{proyecto_id}/herramientas",
        status_code=303
    )


@app.post("/herramientas/{herramienta_id}/estado")
def cambiar_estado_herramienta_ruta(
    herramienta_id: int,
    activa: int = Form(...)
):
    herramienta = obtener_herramienta_por_id(herramienta_id)

    if herramienta:
        proyecto_id = herramienta[1]

        cambiar_estado_herramienta(
            herramienta_id,
            bool(activa)
        )

        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/herramientas",
            status_code=303
        )

    return RedirectResponse(
        url="/proyectos",
        status_code=303
    )


@app.post("/herramientas/{herramienta_id}/eliminar")
def eliminar_herramienta_ruta(
    herramienta_id: int
):
    herramienta = obtener_herramienta_por_id(herramienta_id)

    if herramienta:
        proyecto_id = herramienta[1]

        eliminar_herramienta_proyecto(herramienta_id)

        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/herramientas",
            status_code=303
        )

    return RedirectResponse(
        url="/proyectos",
        status_code=303
    )

@app.post("/proyectos/{id}/funciones/{funcion_id}/agregar")
async def agregar_funcion_al_proyecto(
    id: int,
    funcion_id: int
):
    asignar_funcion_proyecto(
        proyecto_id=id,
        funcion_id=funcion_id
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/funciones",
        status_code=303
    )


@app.post("/proyectos/{id}/funciones/{relacion_id}/estado")
async def cambiar_estado_funcion_del_proyecto(
    id: int,
    relacion_id: int,
    request: Request
):
    formulario = await request.form()

    activa = formulario.get("activa") == "1"

    cambiar_estado_funcion_proyecto(
        relacion_id=relacion_id,
        activa=activa
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/funciones",
        status_code=303
    )


@app.post("/proyectos/{id}/funciones/{relacion_id}/quitar")
async def quitar_funcion_del_proyecto(
    id: int,
    relacion_id: int
):
    quitar_funcion_proyecto(
        relacion_id=relacion_id
    )

    return RedirectResponse(
        url=f"/proyectos/{id}/funciones",
        status_code=303
    )


@app.get("/herramientas/{herramienta_id}/acciones")
def ver_acciones_herramienta(
    request: Request,
    herramienta_id: int
):
    herramienta = obtener_herramienta_por_id(herramienta_id)

    if not herramienta:
        return RedirectResponse(
            url="/proyectos",
            status_code=303
        )

    proyecto_id = herramienta[1]

    acciones = obtener_acciones_herramienta(herramienta_id)

    return templates.TemplateResponse(
        request=request,
        name="acciones_herramienta.html",
        context={
            "herramienta": herramienta,
            "proyecto_id": proyecto_id,
            "acciones": acciones
        }
    )


@app.post("/herramientas/{herramienta_id}/acciones/guardar")
def guardar_accion(
    herramienta_id: int,
    nombre: str = Form(...),
    codigo: str = Form(...),
    descripcion: str = Form(""),
    parametros: str = Form("")
):
    herramienta = obtener_herramienta_por_id(herramienta_id)

    if not herramienta:
        return RedirectResponse(
            url="/proyectos",
            status_code=303
        )

    guardar_accion_herramienta(
        herramienta_id,
        nombre,
        codigo,
        descripcion,
        parametros
    )

    return RedirectResponse(
        url=f"/herramientas/{herramienta_id}/acciones",
        status_code=303
    )


@app.post("/acciones/{accion_id}/estado")
def cambiar_estado_accion_ruta(
    accion_id: int,
    activa: int = Form(...)
):
    accion = obtener_accion_por_id(accion_id)

    if not accion:
        return RedirectResponse(
            url="/proyectos",
            status_code=303
        )

    herramienta_id = accion[1]

    cambiar_estado_accion(
        accion_id,
        bool(activa)
    )

    return RedirectResponse(
        url=f"/herramientas/{herramienta_id}/acciones",
        status_code=303
    )


@app.post("/acciones/{accion_id}/eliminar")
def eliminar_accion_ruta(
    accion_id: int
):
    accion = obtener_accion_por_id(accion_id)

    if not accion:
        return RedirectResponse(
            url="/proyectos",
            status_code=303
        )

    herramienta_id = accion[1]

    eliminar_accion_herramienta(accion_id)

    return RedirectResponse(
        url=f"/herramientas/{herramienta_id}/acciones",
        status_code=303
    )


@app.get("/funciones/{funcion_id}/acciones")
def ver_acciones_funcion(
    request: Request,
    funcion_id: int
):
    acciones_asignadas = obtener_acciones_de_funcion(funcion_id)

    acciones_disponibles = (
        obtener_acciones_disponibles_para_funcion(funcion_id)
    )

    return templates.TemplateResponse(
        request=request,
        name="acciones_funcion.html",
        context={
            "funcion_id": funcion_id,
            "acciones_asignadas": acciones_asignadas,
            "acciones_disponibles": acciones_disponibles
        }
    )


@app.post("/funciones/{funcion_id}/acciones/asignar")
def asignar_accion_funcion(
    funcion_id: int,
    accion_id: int = Form(...)
):
    asignar_accion_a_funcion(
        funcion_id,
        accion_id
    )

    return RedirectResponse(
        url=f"/funciones/{funcion_id}/acciones",
        status_code=303
    )


@app.post("/funciones/acciones/{relacion_id}/estado")
def cambiar_estado_accion_funcion_ruta(
    relacion_id: int,
    funcion_id: int = Form(...),
    activa: int = Form(...)
):
    cambiar_estado_accion_funcion(
        relacion_id,
        bool(activa)
    )

    return RedirectResponse(
        url=f"/funciones/{funcion_id}/acciones",
        status_code=303
    )


@app.post("/funciones/acciones/{relacion_id}/quitar")
def quitar_accion_funcion_ruta(
    relacion_id: int,
    funcion_id: int = Form(...)
):
    quitar_accion_de_funcion(relacion_id)

    return RedirectResponse(
        url=f"/funciones/{funcion_id}/acciones",
        status_code=303
    )


@app.get("/funciones/{funcion_id}/capacidades")
def ver_capacidades_funcion(
    request: Request,
    funcion_id: int
):
    capacidades = obtener_capacidades_funcion(funcion_id)

    return templates.TemplateResponse(
        request=request,
        name="capacidades_funcion.html",
        context={
            "funcion_id": funcion_id,
            "capacidades": capacidades
        }
    )


@app.get("/proyectos/{proyecto_id}/capacidades")
def ver_capacidades_proyecto(
    request: Request,
    proyecto_id: int
):
    capacidades = obtener_capacidades_proyecto(proyecto_id)

    return templates.TemplateResponse(
        request=request,
        name="capacidades_proyecto.html",
        context={
            "proyecto_id": proyecto_id,
            "capacidades": capacidades
        }
    )


# =========================================================
# ESTACIÓN 12 — NIVEL 1
# INTENCIONES DEL PROYECTO
# =========================================================


@app.get("/proyectos/{proyecto_id}/intenciones")
def ver_intenciones_proyecto(
    request: Request,
    proyecto_id: int
):
    proyectos = obtener_proyectos()

    proyecto = next(
        (
            proyecto
            for proyecto in proyectos
            if proyecto[0] == proyecto_id
        ),
        None
    )

    intenciones_proyecto = (
        obtener_intenciones_proyecto(
            proyecto_id
        )
    )

    intenciones_disponibles = (
        obtener_intenciones_disponibles(
            proyecto_id
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="intenciones_proyecto.html",
        context={
            "proyecto": proyecto,
            "intenciones_proyecto": intenciones_proyecto,
            "intenciones_disponibles": intenciones_disponibles
        }
    )


@app.post(
    "/proyectos/{proyecto_id}/intenciones/{intencion_id}/agregar"
)
def agregar_intencion_a_proyecto(
    proyecto_id: int,
    intencion_id: int
):
    agregar_intencion_proyecto(
        proyecto_id,
        intencion_id
    )

    return RedirectResponse(
        url=f"/proyectos/{proyecto_id}/intenciones",
        status_code=303
    )


@app.post(
    "/proyectos/{proyecto_id}/intenciones/{intencion_id}/estado"
)
async def cambiar_estado_intencion_del_proyecto(
    request: Request,
    proyecto_id: int,
    intencion_id: int
):
    formulario = await request.form()

    activa = (
        formulario.get("activa") == "1"
    )

    cambiar_estado_intencion_proyecto(
        proyecto_id,
        intencion_id,
        activa
    )

    return RedirectResponse(
        url=f"/proyectos/{proyecto_id}/intenciones",
        status_code=303
    )


@app.post(
    "/proyectos/{proyecto_id}/intenciones/{intencion_id}/prioridad"
)
async def cambiar_prioridad_intencion_del_proyecto(
    request: Request,
    proyecto_id: int,
    intencion_id: int
):
    formulario = await request.form()

    prioridad = int(
        formulario.get("prioridad") or 0
    )

    actualizar_prioridad_intencion_proyecto(
        proyecto_id,
        intencion_id,
        prioridad
    )

    return RedirectResponse(
        url=f"/proyectos/{proyecto_id}/intenciones",
        status_code=303
    )


@app.post(
    "/proyectos/{proyecto_id}/intenciones/{intencion_id}/quitar"
)
def quitar_intencion_del_proyecto(
    proyecto_id: int,
    intencion_id: int
):
    quitar_intencion_proyecto(
        proyecto_id,
        intencion_id
    )

    return RedirectResponse(
        url=f"/proyectos/{proyecto_id}/intenciones",
        status_code=303
    )


# =========================================================
# ESTACIÓN 12 — NIVEL 1
# PATRONES DE INTENCIÓN
# =========================================================


@app.get("/intenciones/{intencion_id}/patrones")
def ver_patrones_intencion(
    request: Request,
    intencion_id: int
):
    intencion = obtener_intencion(
        intencion_id
    )

    patrones = obtener_patrones_intencion(
        intencion_id
    )

    return templates.TemplateResponse(
        request=request,
        name="patrones_intencion.html",
        context={
            "intencion": intencion,
            "patrones": patrones
        }
    )


@app.post("/intenciones/{intencion_id}/patrones/guardar")
async def guardar_patron_intencion(
    request: Request,
    intencion_id: int
):
    formulario = await request.form()

    patron = formulario.get("patron")

    tipo = formulario.get("tipo") or "FRASE"

    prioridad = int(
        formulario.get("prioridad") or 0
    )

    crear_patron_intencion(
        intencion_id=intencion_id,
        patron=patron,
        tipo=tipo,
        prioridad=prioridad,
        activo=True
    )

    return RedirectResponse(
        url=f"/intenciones/{intencion_id}/patrones",
        status_code=303
    )


@app.post("/intenciones/{intencion_id}/patrones/{patron_id}/actualizar")
async def actualizar_patron_intencion_ruta(
    request: Request,
    intencion_id: int,
    patron_id: int
):
    formulario = await request.form()

    patron = formulario.get("patron")

    tipo = formulario.get("tipo")

    prioridad = int(
        formulario.get("prioridad") or 0
    )

    activo = (
        formulario.get("activo") == "1"
    )

    actualizar_patron_intencion(
        patron_id=patron_id,
        patron=patron,
        tipo=tipo,
        prioridad=prioridad,
        activo=activo
    )

    return RedirectResponse(
        url=f"/intenciones/{intencion_id}/patrones",
        status_code=303
    )


@app.post("/intenciones/{intencion_id}/patrones/{patron_id}/eliminar")
def eliminar_patron_intencion_ruta(
    intencion_id: int,
    patron_id: int
):
    eliminar_patron_intencion(
        patron_id
    )

    return RedirectResponse(
        url=f"/intenciones/{intencion_id}/patrones",
        status_code=303
    )


@app.get("/autenticacion/instagram/callback")
async def retorno_inicio_sesion_instagram(request: Request):
    """Recibe el retorno de Meta tras autorizar Instagram."""
    parametros = request.query_params
    error = parametros.get("error")
    codigo = parametros.get("code")

    if error:
        return HTMLResponse(
            content="<h1>La autorización de Instagram fue cancelada.</h1>",
            status_code=400,
        )

    if not codigo:
        return HTMLResponse(
            content="<h1>No se recibió un código de autorización.</h1>",
            status_code=400,
        )

    return HTMLResponse(
        content=(
            "<h1>Instagram autorizado correctamente.</h1>"
            "<p>Podés volver a la plataforma.</p>"
        ),
        status_code=200,
    )
