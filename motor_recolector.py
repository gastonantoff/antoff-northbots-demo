import sqlite3

from db_manager import (
    DB_NAME,
    obtener_proyecto_por_id,
    obtener_items_catalogo,
    obtener_conocimiento,
    obtener_personalidad,
    obtener_capacidades,
    obtener_configuracion_ia,
    obtener_canales,
    obtener_accesos,
    obtener_flujos,
    obtener_funciones_proyecto,
    obtener_intenciones_proyecto,
    obtener_requisitos_intencion,
    obtener_patrones_intencion,
    obtener_herramientas_proyecto,
    obtener_acciones_herramienta,
    obtener_capacidades_proyecto
)


def obtener_empresa_proyecto(proyecto_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            nombre,
            rubro,
            whatsapp,
            direccion,
            horario,
            sitio_web,
            observaciones
        FROM empresa_proyecto
        WHERE proyecto_id = ?
    """, (proyecto_id,))

    empresa = cursor.fetchone()

    conexion.close()

    return empresa


def convertir_proyecto(proyecto):
    if not proyecto:
        return None

    return {
        "id": proyecto[0],
        "nombre": proyecto[1],
        "cliente": proyecto[2],
        "empresa": proyecto[3],
        "rubro": proyecto[4],
        "estado": proyecto[5],
        "fecha_creacion": proyecto[6],
        "fecha_actualizacion": proyecto[7],
        "observaciones": proyecto[8]
    }


def convertir_empresa(empresa):
    if not empresa:
        return None

    return {
        "id": empresa[0],
        "proyecto_id": empresa[1],
        "nombre": empresa[2],
        "rubro": empresa[3],
        "whatsapp": empresa[4],
        "direccion": empresa[5],
        "horario": empresa[6],
        "sitio_web": empresa[7],
        "observaciones": empresa[8]
    }


def convertir_catalogo(items):
    resultado = []

    for item in items:
        resultado.append({
            "id": item[0],
            "tipo": item[1],
            "categoria": item[2],
            "nombre": item[3],
            "descripcion": item[4],
            "precio": item[5],
            "observaciones": item[6]
        })

    return resultado


def convertir_conocimiento(items):
    resultado = []

    for item in items:
        resultado.append({
            "id": item[0],
            "categoria": item[1],
            "titulo": item[2],
            "contenido": item[3],
            "observaciones": item[4]
        })

    return resultado


def convertir_personalidad(personalidad):
    if not personalidad:
        return None

    return {
        "id": personalidad[0],
        "proyecto_id": personalidad[1],
        "nombre": personalidad[2],
        "rol": personalidad[3],
        "objetivo": personalidad[4],
        "comunicacion": personalidad[5],
        "iniciativa": personalidad[6],
        "longitud_respuestas": personalidad[7],
        "emojis": personalidad[8],
        "restricciones": personalidad[9],
        "despedida": personalidad[10]
    }


def convertir_configuracion_ia(configuracion):
    if not configuracion:
        return None

    return {
        "id": configuracion[0],
        "proyecto_id": configuracion[1],
        "modelo": configuracion[2],
        "razonamiento": configuracion[3],
        "creatividad": configuracion[4],
        "longitud": configuracion[5],
        "iniciativa": configuracion[6],
        "autonomia": configuracion[7],
        "prioridad": configuracion[8],
        "memoria": configuracion[9]
    }


def convertir_accesos(accesos):
    resultado = []

    for acceso in accesos:
        resultado.append({
            "id": acceso[0],
            "proyecto_id": acceso[1],
            "nombre_recurso": acceso[2],
            "tipo_recurso": acceso[3],
            "ubicacion": acceso[4],
            "permiso": acceso[5],
            "descripcion": acceso[6],
            "activo": acceso[7],
            "fecha_creacion": acceso[8],
            "fecha_actualizacion": acceso[9]
        })

    return resultado


def convertir_flujos(flujos):
    resultado = []

    for flujo in flujos:
        resultado.append({
            "id": flujo[0],
            "proyecto_id": flujo[1],
            "nombre": flujo[2],
            "descripcion": flujo[3],
            "disparador": flujo[4],
            "condicion": flujo[5],
            "accion": flujo[6],
            "prioridad": flujo[7],
            "activo": flujo[8],
            "fecha_creacion": flujo[9],
            "fecha_actualizacion": flujo[10]
        })

    return resultado


def convertir_funciones(funciones):
    resultado = []

    for funcion in funciones:
        resultado.append({
            "id": funcion[0],
            "proyecto_id": funcion[1],
            "funcion_id": funcion[2],
            "nombre": funcion[3],
            "categoria": funcion[4],
            "descripcion": funcion[5],
            "objetivo": funcion[6],
            "estrategia_resolucion": funcion[7],
            "derivacion_humana": funcion[8],
            "activa": funcion[9]
        })

    return resultado


def convertir_intenciones(intenciones):
    resultado = []

    for intencion in intenciones:

        intencion_id = intencion[2]

        patrones_bd = obtener_patrones_intencion(
            intencion_id
        )

        requisitos_bd = obtener_requisitos_intencion(
            intencion_id
        )

        patrones = []

        for patron in patrones_bd:
            patrones.append({
                "id": patron[0],
                "intencion_id": patron[1],
                "patron": patron[2],
                "tipo": patron[3],
                "prioridad": patron[4],
                "activo": patron[5],
                "fecha_creacion": patron[6],
                "fecha_actualizacion": patron[7]
            })

        requisitos = []

        for requisito in requisitos_bd:
            requisitos.append({
                "id": requisito[0],
                "intencion_id": requisito[1],
                "codigo": requisito[2],
                "nombre": requisito[3],
                "tipo": requisito[4],
                "obligatorio": requisito[5],
                "prioridad": requisito[6],
                "descripcion": requisito[7],
                "activo": requisito[8],
                "fecha_creacion": requisito[9],
                "fecha_actualizacion": requisito[10]
            })

        resultado.append({
            "id": intencion[0],
            "proyecto_id": intencion[1],
            "intencion_id": intencion[2],
            "nombre": intencion[3],
            "codigo": intencion[4],
            "descripcion": intencion[5],
            "categoria": intencion[6],
            "prioridad": intencion[7],
            "requiere_contexto": intencion[8],
            "permite_derivacion": intencion[9],
            "activa": intencion[10],
            "patrones": patrones,
            "requisitos": requisitos
        })

    return resultado


def convertir_herramientas(herramientas):
    resultado = []

    for herramienta in herramientas:

        herramienta_id = herramienta[0]

        acciones_bd = obtener_acciones_herramienta(
            herramienta_id
        )

        acciones = []

        for accion in acciones_bd:
            acciones.append({
                "id": accion[0],
                "nombre": accion[1],
                "operacion": accion[2],
                "descripcion": accion[3],
                "parametros": accion[4],
                "activo": accion[5]
            })

        resultado.append({
            "id": herramienta[0],
            "nombre": herramienta[1],
            "tipo": herramienta[2],
            "descripcion": herramienta[3],
            "configuracion": herramienta[4],
            "activo": herramienta[5],
            "acciones": acciones
        })

    return resultado


def convertir_capacidades(capacidades):
    resultado = []

    for capacidad in capacidades:
        resultado.append({
            "funcion_id": capacidad[0],
            "funcion_nombre": capacidad[1],
            "accion_id": capacidad[2],
            "accion_nombre": capacidad[3],
            "operacion": capacidad[4],
            "accion_descripcion": capacidad[5],
            "herramienta_id": capacidad[6],
            "herramienta_nombre": capacidad[7],
            "herramienta_tipo": capacidad[8],
            "proveedor": capacidad[9]
        })

    return resultado


def recolectar_proyecto(proyecto_id):

    proyecto = obtener_proyecto_por_id(
        proyecto_id
    )

    if proyecto is None:
        return None

    empresa = obtener_empresa_proyecto(
        proyecto_id
    )

    # Compatibilidad: algunos proyectos antiguos guardan
    # empresa/rubro directamente en la tabla proyectos.
    if not empresa:
        empresa = (
            proyecto[0],
            proyecto[0],
            proyecto[3],
            proyecto[4],
            None,
            None,
            None,
            None,
            proyecto[8],
        )

    catalogo = obtener_items_catalogo(
        proyecto_id
    )

    conocimiento = obtener_conocimiento(
        proyecto_id
    )

    personalidad = obtener_personalidad(
        proyecto_id
    )

    capacidades = obtener_capacidades(
        proyecto_id
    )

    configuracion_ia = obtener_configuracion_ia(
        proyecto_id
    )

    canales = obtener_canales(
        proyecto_id
    )

    accesos = obtener_accesos(
        proyecto_id
    )

    flujos = obtener_flujos(
        proyecto_id
    )

    funciones = obtener_funciones_proyecto(
        proyecto_id
    )

    intenciones = obtener_intenciones_proyecto(
        proyecto_id
    )

    herramientas = obtener_herramientas_proyecto(
        proyecto_id
    )

    capacidades_detalladas = obtener_capacidades_proyecto(
        proyecto_id
    )

    return {
        "proyecto": convertir_proyecto(
            proyecto
        ),

        "empresa": convertir_empresa(
            empresa
        ),

        "catalogo": convertir_catalogo(
            catalogo
        ),

        "conocimiento": convertir_conocimiento(
            conocimiento
        ),

        "personalidad": convertir_personalidad(
            personalidad
        ),

        "capacidades": capacidades,

        "configuracion_ia": convertir_configuracion_ia(
            configuracion_ia
        ),

        "canales": canales,

        "accesos": convertir_accesos(
            accesos
        ),

        "flujos": convertir_flujos(
            flujos
        ),

        "funciones": convertir_funciones(
            funciones
        ),

        "intenciones": convertir_intenciones(
            intenciones
        ),

        "herramientas": convertir_herramientas(
            herramientas
        ),

        "capacidades_detalladas": convertir_capacidades(
            capacidades_detalladas
        )
    }