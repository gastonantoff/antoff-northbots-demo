import sqlite3
import json

DB_NAME = "negocios.db"

def crear_base():
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()


    cursor.execute("""
        PRAGMA table_info(acciones_herramienta)
    """)

    print("COLUMNAS ACCIONES:")
    print(cursor.fetchall())

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS negocios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            rubro TEXT NOT NULL,
            whatsapp TEXT NOT NULL,
            horario TEXT NOT NULL,
            direccion TEXT NOT NULL
        )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS perfiles_negocio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        negocio_id INTEGER NOT NULL UNIQUE,
        descripcion TEXT,
        productos_servicios TEXT,
        formas_pago TEXT,
        entregas_reservas TEXT,
        informacion_adicional TEXT,
        FOREIGN KEY (negocio_id) REFERENCES negocios(id)
    )
""")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos_servicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        negocio_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio REAL,
        tipo TEXT NOT NULL,
        FOREIGN KEY (negocio_id) REFERENCES negocios(id)
    )
""")
 

    cursor.execute("""
CREATE TABLE IF NOT EXISTS proyectos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cliente TEXT NOT NULL,
    empresa TEXT NOT NULL,
    rubro TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'Nuevo',
    fecha_creacion TEXT,
    fecha_actualizacion TEXT,
    observaciones TEXT
)
""")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empresa_proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proyecto_id INTEGER NOT NULL UNIQUE,
        nombre TEXT,
        rubro TEXT,
        whatsapp TEXT,
        direccion TEXT,
        horario TEXT,
        sitio_web TEXT,
        observaciones TEXT,
        FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS catalogo_proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proyecto_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        categoria TEXT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio REAL,
        observaciones TEXT,
        FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
    )
    """)


    cursor.execute("""
CREATE TABLE IF NOT EXISTS conocimiento_proyecto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proyecto_id INTEGER NOT NULL,

    categoria TEXT,
    titulo TEXT,
    contenido TEXT,
    observaciones TEXT,

    FOREIGN KEY (proyecto_id)
    REFERENCES proyectos(id)
)
""")


    cursor.execute("""
CREATE TABLE IF NOT EXISTS personalidad_proyecto (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    proyecto_id INTEGER NOT NULL,

    nombre TEXT,

    rol TEXT,

    objetivo TEXT,

    comunicacion TEXT,

    iniciativa TEXT,

    longitud_respuestas TEXT,

    emojis TEXT,

    restricciones TEXT,

    despedida TEXT,

    FOREIGN KEY (proyecto_id)
    REFERENCES proyectos(id)

)
""")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS capacidades_proyecto (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        proyecto_id INTEGER NOT NULL,

        capacidad TEXT NOT NULL,

        FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id)

    )
""")
    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracion_ia_proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proyecto_id INTEGER NOT NULL UNIQUE,

        modelo TEXT,
        razonamiento TEXT,
        creatividad TEXT,
        longitud TEXT,
        iniciativa TEXT,
        autonomia TEXT,
        prioridad TEXT,
        memoria TEXT,

        FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id)
)
""")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canales_proyecto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proyecto_id INTEGER NOT NULL,
    canal TEXT NOT NULL,

    FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id),

    UNIQUE(proyecto_id, canal)
);
""")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistentes_proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        proyecto_id INTEGER NOT NULL UNIQUE,

        nombre TEXT,
        instrucciones TEXT,
        configuracion TEXT,

        estado TEXT NOT NULL DEFAULT 'No generado',

        fecha_generacion TEXT,
        fecha_actualizacion TEXT,

        FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accesos_proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        proyecto_id INTEGER NOT NULL,

        nombre_recurso TEXT NOT NULL,

        tipo_recurso TEXT NOT NULL,

        ubicacion TEXT,

        permiso TEXT NOT NULL DEFAULT 'lectura',

        descripcion TEXT,

        activo INTEGER NOT NULL DEFAULT 1,

        fecha_creacion TEXT,

        fecha_actualizacion TEXT,

        FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flujos_proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        proyecto_id INTEGER NOT NULL,

        nombre TEXT NOT NULL,

        descripcion TEXT,

        disparador TEXT NOT NULL,

        condicion TEXT,

        accion TEXT NOT NULL,

        prioridad INTEGER NOT NULL DEFAULT 0,

        activo INTEGER NOT NULL DEFAULT 1,

        fecha_creacion TEXT,

        fecha_actualizacion TEXT,

        FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funciones_catalogo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nombre TEXT NOT NULL,

        categoria TEXT NOT NULL,

        descripcion TEXT,

        objetivo TEXT,

        estrategia_resolucion TEXT,

        derivacion_humana INTEGER NOT NULL DEFAULT 1,

        activa INTEGER NOT NULL DEFAULT 1,

        fecha_creacion TEXT,

        fecha_actualizacion TEXT
    )
    """)


        # MIGRACION ESTACION 11
    # Reconstruimos funciones_proyecto para eliminar
    # la estructura antigua y usar funcion_id.

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funciones_proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        proyecto_id INTEGER NOT NULL,

        funcion_id INTEGER NOT NULL,

        activa INTEGER NOT NULL DEFAULT 1,

        fecha_creacion TEXT,

        fecha_actualizacion TEXT,

        FOREIGN KEY (proyecto_id)
            REFERENCES proyectos(id),

        FOREIGN KEY (funcion_id)
            REFERENCES funciones_catalogo(id),

        UNIQUE(proyecto_id, funcion_id)
    )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS herramientas_proyecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            proyecto_id INTEGER NOT NULL,

            nombre TEXT NOT NULL,

            tipo TEXT NOT NULL,

            descripcion TEXT,

            configuracion TEXT,

            activa INTEGER NOT NULL DEFAULT 1,

            fecha_creacion TEXT,

            fecha_actualizacion TEXT,

            FOREIGN KEY (proyecto_id)
                REFERENCES proyectos(id)
        )
    """)


    cursor.execute("""
        PRAGMA table_info(herramientas_proyecto)
    """)

    columnas_herramientas = [
        columna[1]
        for columna in cursor.fetchall()
    ]

    if "configuracion" not in columnas_herramientas:
        cursor.execute("""
            ALTER TABLE herramientas_proyecto
            ADD COLUMN configuracion TEXT
        """)

        # =========================================================
    # ESTACIÓN 12 — NIVEL 1
    # INTENCIONES
    # =========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intenciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre TEXT NOT NULL,

            codigo TEXT NOT NULL UNIQUE,

            descripcion TEXT,

            categoria TEXT,

            prioridad INTEGER NOT NULL DEFAULT 0,

            requiere_contexto INTEGER NOT NULL DEFAULT 0,

            permite_derivacion INTEGER NOT NULL DEFAULT 1,

            activa INTEGER NOT NULL DEFAULT 1,

            fecha_creacion TEXT,

            fecha_actualizacion TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intenciones_proyecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            proyecto_id INTEGER NOT NULL,

            intencion_id INTEGER NOT NULL,

            activa INTEGER NOT NULL DEFAULT 1,

            prioridad INTEGER NOT NULL DEFAULT 0,

            fecha_creacion TEXT,

            fecha_actualizacion TEXT,

            FOREIGN KEY (proyecto_id)
                REFERENCES proyectos(id),

            FOREIGN KEY (intencion_id)
                REFERENCES intenciones(id),

            UNIQUE(proyecto_id, intencion_id)
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patrones_intencion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            intencion_id INTEGER NOT NULL,

            patron TEXT NOT NULL,

            tipo TEXT NOT NULL DEFAULT 'FRASE',

            prioridad INTEGER NOT NULL DEFAULT 0,

            activo INTEGER NOT NULL DEFAULT 1,

            fecha_creacion TEXT,

            fecha_actualizacion TEXT,

            FOREIGN KEY (intencion_id)
                REFERENCES intenciones(id)
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acciones_herramienta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            herramienta_id INTEGER NOT NULL,

            nombre TEXT NOT NULL,

            codigo TEXT NOT NULL,

            descripcion TEXT,

            parametros TEXT,

            activa INTEGER NOT NULL DEFAULT 1,

            fecha_creacion TEXT,

            fecha_actualizacion TEXT,

            FOREIGN KEY (herramienta_id)
                REFERENCES herramientas_proyecto(id),

            UNIQUE(herramienta_id, codigo)
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funciones_acciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            funcion_id INTEGER NOT NULL,

            accion_id INTEGER NOT NULL,

            activa INTEGER NOT NULL DEFAULT 1,

            fecha_creacion TEXT,
            fecha_actualizacion TEXT,

            FOREIGN KEY (funcion_id)
                REFERENCES funciones_catalogo(id),

            FOREIGN KEY (accion_id)
                REFERENCES acciones_herramienta(id),

            UNIQUE(funcion_id, accion_id)
        )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requisitos_intencion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        intencion_id INTEGER NOT NULL,

        codigo TEXT NOT NULL,

        nombre TEXT NOT NULL,

        tipo TEXT NOT NULL DEFAULT 'texto',

        obligatorio INTEGER NOT NULL DEFAULT 1,

        prioridad INTEGER NOT NULL DEFAULT 0,

        descripcion TEXT,

        activo INTEGER NOT NULL DEFAULT 1,

        fecha_creacion TEXT,

        fecha_actualizacion TEXT,

        FOREIGN KEY (intencion_id)
            REFERENCES intenciones(id),

        UNIQUE(intencion_id, codigo)
    )
""")
            
    conexion.commit()
    conexion.close()
   

def guardar_negocio(nombre, rubro, whatsapp, horario, direccion):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO negocios
        (nombre, rubro, whatsapp, horario, direccion)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, rubro, whatsapp, horario, direccion))

    conexion.commit()
    conexion.close()


def obtener_negocios():
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, rubro, whatsapp, horario, direccion
        FROM negocios
        ORDER BY id DESC
    """)

    negocios = cursor.fetchall()

    conexion.close()

    return negocios


def obtener_negocio_por_id(id):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, rubro, whatsapp, horario, direccion
        FROM negocios
        WHERE id = ?
    """, (id,))

    negocio = cursor.fetchone()

    conexion.close()

    return negocio


def actualizar_negocio(id, nombre, rubro, whatsapp, horario, direccion):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE negocios
        SET nombre = ?,
            rubro = ?,
            whatsapp = ?,
            horario = ?,
            direccion = ?
        WHERE id = ?
    """, (nombre, rubro, whatsapp, horario, direccion, id))

    conexion.commit()
    conexion.close()


def eliminar_negocio(id):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM negocios
        WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()


def guardar_perfil_negocio(
    negocio_id,
    descripcion,
    productos_servicios,
    formas_pago,
    entregas_reservas,
    informacion_adicional
):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO perfiles_negocio (
            negocio_id,
            descripcion,
            productos_servicios,
            formas_pago,
            entregas_reservas,
            informacion_adicional
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(negocio_id) DO UPDATE SET
            descripcion = excluded.descripcion,
            productos_servicios = excluded.productos_servicios,
            formas_pago = excluded.formas_pago,
            entregas_reservas = excluded.entregas_reservas,
            informacion_adicional = excluded.informacion_adicional
    """, (
        negocio_id,
        descripcion,
        productos_servicios,
        formas_pago,
        entregas_reservas,
        informacion_adicional
    ))

    conexion.commit()
    conexion.close()


def obtener_perfil_negocio(negocio_id):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            negocio_id,
            descripcion,
            productos_servicios,
            formas_pago,
            entregas_reservas,
            informacion_adicional
        FROM perfiles_negocio
        WHERE negocio_id = ?
    """, (negocio_id,))

    perfil = cursor.fetchone()

    conexion.close()

    return perfil


def agregar_producto_servicio(
    negocio_id,
    nombre,
    descripcion,
    precio,
    tipo
):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO productos_servicios (
            negocio_id,
            nombre,
            descripcion,
            precio,
            tipo
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        negocio_id,
        nombre,
        descripcion,
        precio,
        tipo
    ))

    conexion.commit()
    conexion.close()


def obtener_productos_servicios(negocio_id):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            negocio_id,
            nombre,
            descripcion,
            precio,
            tipo
        FROM productos_servicios
        WHERE negocio_id = ?
        ORDER BY id DESC
    """, (negocio_id,))

    productos = cursor.fetchall()

    conexion.close()

    return productos


def eliminar_producto_servicio(id):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM productos_servicios
        WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()


def obtener_producto_servicio_por_id(id):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            negocio_id,
            nombre,
            descripcion,
            precio,
            tipo
        FROM productos_servicios
        WHERE id = ?
    """, (id,))

    producto = cursor.fetchone()

    conexion.close()

    return producto


def actualizar_producto_servicio(
    id,
    nombre,
    descripcion,
    precio,
    tipo
):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE productos_servicios
        SET
            nombre = ?,
            descripcion = ?,
            precio = ?,
            tipo = ?
        WHERE id = ?
    """, (
        nombre,
        descripcion,
        precio,
        tipo,
        id
    ))

    conexion.commit()
    conexion.close()


def guardar_proyecto(
    nombre,
    cliente,
    empresa,
    rubro,
    estado="Nuevo",
    observaciones=""
):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO proyectos (
            nombre,
            cliente,
            empresa,
            rubro,
            estado,
            observaciones,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        nombre,
        cliente,
        empresa,
        rubro,
        estado,
        observaciones
    ))

    proyecto_id = cursor.lastrowid
    conexion.commit()
    conexion.close()

    return proyecto_id


def actualizar_proyecto(
    proyecto_id,
    nombre,
    cliente,
    empresa,
    rubro,
    estado,
    observaciones=""
):
    """Actualiza los datos administrativos de un proyecto cliente."""
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE proyectos
        SET
            nombre = ?,
            cliente = ?,
            empresa = ?,
            rubro = ?,
            estado = ?,
            observaciones = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        nombre,
        cliente,
        empresa,
        rubro,
        estado,
        observaciones,
        proyecto_id,
    ))

    actualizado = cursor.rowcount > 0
    conexion.commit()
    conexion.close()

    return actualizado

def guardar_empresa_proyecto(
    proyecto_id,
    nombre,
    rubro,
    whatsapp,
    direccion,
    horario,
    sitio_web,
    observaciones
):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO empresa_proyecto (
            proyecto_id,
            nombre,
            rubro,
            whatsapp,
            direccion,
            horario,
            sitio_web,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        proyecto_id,
        nombre,
        rubro,
        whatsapp,
        direccion,
        horario,
        sitio_web,
        observaciones
    ))

    conexion.commit()
    conexion.close()


def obtener_empresa_proyecto(proyecto_id):
    """Devuelve la ficha del negocio vinculada a un proyecto de asistente."""
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


def obtener_proyectos():
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM proyectos
        ORDER BY id DESC
    """)

    proyectos = cursor.fetchall()

    conexion.close()

    return proyectos


def obtener_proyecto_por_id(id):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM proyectos
        WHERE id = ?
    """, (id,))

    proyecto = cursor.fetchone()

    print(proyecto)

    conexion.close()

    return proyecto


def guardar_item_catalogo(
    proyecto_id,
    tipo,
    categoria,
    nombre,
    descripcion,
    precio,
    observaciones
):
    conexion = sqlite3.connect("negocios.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO catalogo_proyecto (
            proyecto_id,
            tipo,
            categoria,
            nombre,
            descripcion,
            precio,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        proyecto_id,
        tipo,
        categoria,
        nombre,
        descripcion,
        precio,
        observaciones
    ))

    conexion.commit()
    conexion.close()

print("DB_MANAGER CARGADO")
print("guardar_item_catalogo" in globals())

def obtener_items_catalogo(proyecto_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            tipo,
            categoria,
            nombre,
            descripcion,
            precio,
            observaciones
        FROM catalogo_proyecto
        WHERE proyecto_id = ?
        ORDER BY id DESC
    """, (proyecto_id,))

    datos = cursor.fetchall()

    conexion.close()

    return datos


def obtener_item_catalogo_por_id(item_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            tipo,
            categoria,
            nombre,
            descripcion,
            precio,
            observaciones
        FROM catalogo_proyecto
        WHERE id = ?
    """, (item_id,))

    dato = cursor.fetchone()

    conexion.close()

    return dato


def actualizar_item_catalogo(
    item_id,
    tipo,
    categoria,
    nombre,
    descripcion,
    precio,
    observaciones
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE catalogo_proyecto
        SET
            tipo = ?,
            categoria = ?,
            nombre = ?,
            descripcion = ?,
            precio = ?,
            observaciones = ?
        WHERE id = ?
    """, (
        tipo,
        categoria,
        nombre,
        descripcion,
        precio,
        observaciones,
        item_id
    ))

    conexion.commit()
    conexion.close()


def eliminar_item_catalogo(item_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM catalogo_proyecto
        WHERE id = ?
    """, (item_id,))

    conexion.commit()
    conexion.close()


def guardar_conocimiento(
    proyecto_id,
    categoria,
    titulo,
    contenido,
    observaciones
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO conocimiento_proyecto (
            proyecto_id,
            categoria,
            titulo,
            contenido,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        proyecto_id,
        categoria,
        titulo,
        contenido,
        observaciones
    ))

    conexion.commit()
    conexion.close()


def obtener_conocimiento(proyecto_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            categoria,
            titulo,
            contenido,
            observaciones
        FROM conocimiento_proyecto
        WHERE proyecto_id = ?
        ORDER BY id DESC
    """, (proyecto_id,))

    datos = cursor.fetchall()

    conexion.close()

    return datos


def obtener_conocimiento_por_id(conocimiento_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            categoria,
            titulo,
            contenido,
            observaciones
        FROM conocimiento_proyecto
        WHERE id = ?
    """, (conocimiento_id,))

    dato = cursor.fetchone()

    conexion.close()

    return dato


def obtener_personalidad(proyecto_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            nombre,
            rol,
            objetivo,
            comunicacion,
            iniciativa,
            longitud_respuestas,
            emojis,
            restricciones,
            despedida
        FROM personalidad_proyecto
        WHERE proyecto_id = ?
    """, (proyecto_id,))

    personalidad = cursor.fetchone()

    conexion.close()

    return personalidad


def guardar_personalidad(
    proyecto_id,
    nombre,
    rol,
    objetivo,
    comunicacion,
    iniciativa,
    longitud_respuestas,
    emojis,
    restricciones,
    despedida
):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id
        FROM personalidad_proyecto
        WHERE proyecto_id = ?
    """, (proyecto_id,))

    existe = cursor.fetchone()

    if existe:

        cursor.execute("""
            UPDATE personalidad_proyecto
            SET
                nombre = ?,
                rol = ?,
                objetivo = ?,
                comunicacion = ?,
                iniciativa = ?,
                longitud_respuestas = ?,
                emojis = ?,
                restricciones = ?,
                despedida = ?
            WHERE proyecto_id = ?
        """, (
            nombre,
            rol,
            objetivo,
            comunicacion,
            iniciativa,
            longitud_respuestas,
            emojis,
            restricciones,
            despedida,
            proyecto_id
        ))

    else:

        cursor.execute("""
            INSERT INTO personalidad_proyecto (
                proyecto_id,
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            proyecto_id,
            nombre,
            rol,
            objetivo,
            comunicacion,
            iniciativa,
            longitud_respuestas,
            emojis,
            restricciones,
            despedida
        ))

    conexion.commit()
    conexion.close()


def guardar_capacidades(
    proyecto_id,
    capacidades
):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM capacidades_proyecto
        WHERE proyecto_id = ?
    """, (proyecto_id,))

    for capacidad in capacidades:

        cursor.execute("""
            INSERT INTO capacidades_proyecto (
                proyecto_id,
                capacidad
            )
            VALUES (?, ?)
        """, (
            proyecto_id,
            capacidad
        ))

    conexion.commit()
    conexion.close()


def obtener_capacidades(proyecto_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT capacidad
        FROM capacidades_proyecto
        WHERE proyecto_id = ?
    """, (proyecto_id,))

    capacidades = cursor.fetchall()

    conexion.close()

    return [fila[0] for fila in capacidades]


def guardar_configuracion_ia(
    proyecto_id,
    modelo,
    razonamiento,
    creatividad,
    longitud,
    iniciativa,
    autonomia,
    prioridad,
    memoria
):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO configuracion_ia_proyecto (
            proyecto_id,
            modelo,
            razonamiento,
            creatividad,
            longitud,
            iniciativa,
            autonomia,
            prioridad,
            memoria
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        proyecto_id,
        modelo,
        razonamiento,
        creatividad,
        longitud,
        iniciativa,
        autonomia,
        prioridad,
        memoria
    ))

    conexion.commit()
    conexion.close()

def obtener_configuracion_ia(proyecto_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            modelo,
            razonamiento,
            creatividad,
            longitud,
            iniciativa,
            autonomia,
            prioridad,
            memoria
        FROM configuracion_ia_proyecto
        WHERE proyecto_id = ?
    """, (proyecto_id,))

    configuracion = cursor.fetchone()

    conexion.close()

    return configuracion


def guardar_canales(proyecto_id, canales):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM canales_proyecto WHERE proyecto_id = ?",
        (proyecto_id,)
    )

    for canal in canales:
        cursor.execute(
            """
            INSERT INTO canales_proyecto
            (proyecto_id, canal)
            VALUES (?, ?)
            """,
            (proyecto_id, canal)
        )

    conexion.commit()
    conexion.close()


def obtener_canales(proyecto_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT canal
        FROM canales_proyecto
        WHERE proyecto_id = ?
        ORDER BY id
        """,
        (proyecto_id,)
    )

    canales = [fila[0] for fila in cursor.fetchall()]

    conexion.close()

    return canales


def guardar_asistente(
    proyecto_id,
    nombre,
    instrucciones,
    configuracion,
    estado="Generado"
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO asistentes_proyecto (
            proyecto_id,
            nombre,
            instrucciones,
            configuracion,
            estado,
            fecha_generacion,
            fecha_actualizacion
        )
        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ON CONFLICT(proyecto_id)
        DO UPDATE SET
            nombre = excluded.nombre,
            instrucciones = excluded.instrucciones,
            configuracion = excluded.configuracion,
            estado = excluded.estado,
            fecha_actualizacion = datetime('now')
    """, (
        proyecto_id,
        nombre,
        instrucciones,
        configuracion,
        estado
    ))

    conexion.commit()
    conexion.close()


def obtener_asistente(proyecto_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            nombre,
            instrucciones,
            configuracion,
            estado,
            fecha_generacion,
            fecha_actualizacion
        FROM asistentes_proyecto
        WHERE proyecto_id = ?
    """, (proyecto_id,))

    asistente = cursor.fetchone()

    conexion.close()

    return asistente


def generar_configuracion_asistente(proyecto_id):

    proyecto = obtener_proyecto_por_id(proyecto_id)

    if proyecto is None:
        return None

    catalogo = obtener_items_catalogo(proyecto_id)

    conocimiento = obtener_conocimiento(proyecto_id)

    personalidad = obtener_personalidad(proyecto_id)

    capacidades = obtener_capacidades(proyecto_id)

    configuracion_ia = obtener_configuracion_ia(proyecto_id)

    canales = obtener_canales(proyecto_id)

    accesos = obtener_accesos(proyecto_id)

    flujos = obtener_flujos(proyecto_id)

    configuracion = {
        "proyecto": {
            "id": proyecto[0],
            "nombre": proyecto[1],
            "cliente": proyecto[2],
            "empresa": proyecto[3],
            "rubro": proyecto[4],
            "estado": proyecto[5],
            "observaciones": proyecto[8]
        },

        "catalogo": [
            {
                "id": item[0],
                "tipo": item[1],
                "categoria": item[2],
                "nombre": item[3],
                "descripcion": item[4],
                "precio": item[5],
                "observaciones": item[6]
            }
            for item in catalogo
        ],

        "conocimiento": [
            {
                "id": item[0],
                "categoria": item[1],
                "titulo": item[2],
                "contenido": item[3],
                "observaciones": item[4]
            }
            for item in conocimiento
        ],

        "personalidad": None,

        "capacidades": capacidades,

        "configuracion_ia": None,

        "canales": canales,

        "accesos": [
            {
                "id": acceso[0],
                "nombre_recurso": acceso[2],
                "tipo_recurso": acceso[3],
                "ubicacion": acceso[4],
                "permiso": acceso[5],
                "descripcion": acceso[6],
                "activo": acceso[7]
            }
            for acceso in accesos
            if acceso[7] == 1
        ],

        "flujos": [
            {
                "id": flujo[0],
                "nombre": flujo[2],
                "descripcion": flujo[3],
                "disparador": flujo[4],
                "condicion": flujo[5],
                "accion": flujo[6],
                "prioridad": flujo[7],
                "activo": flujo[8]
            }
            for flujo in flujos
            if flujo[8] == 1
        ]
    }

    if personalidad:

        configuracion["personalidad"] = {
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

    if configuracion_ia:

        configuracion["configuracion_ia"] = {
            "id": configuracion_ia[0],
            "proyecto_id": configuracion_ia[1],
            "modelo": configuracion_ia[2],
            "razonamiento": configuracion_ia[3],
            "creatividad": configuracion_ia[4],
            "longitud": configuracion_ia[5],
            "iniciativa": configuracion_ia[6],
            "autonomia": configuracion_ia[7],
            "prioridad": configuracion_ia[8],
            "memoria": configuracion_ia[9]
        }

    return configuracion
def generar_asistente(proyecto_id):

    configuracion = generar_configuracion_asistente(proyecto_id)

    if configuracion is None:
        return None

    proyecto = obtener_proyecto_por_id(proyecto_id)

    nombre = proyecto[1]

    instrucciones = f"""
Eres el asistente virtual de {nombre}.

Debes utilizar la información, personalidad, capacidades,
configuración y canales definidos para este proyecto.

Debes responder de acuerdo con la configuración establecida
y respetar las restricciones definidas.
""".strip()

    configuracion_json = json.dumps(
        configuracion,
        ensure_ascii=False,
        indent=4
    )

    guardar_asistente(
        proyecto_id=proyecto_id,
        nombre=f"Asistente {nombre}",
        instrucciones=instrucciones,
        configuracion=configuracion_json,
        estado="Generado"
    )

    return obtener_asistente(proyecto_id)


def guardar_acceso(
    proyecto_id,
    nombre_recurso,
    tipo_recurso,
    ubicacion=None,
    permiso="lectura",
    descripcion=None
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO accesos_proyecto (
            proyecto_id,
            nombre_recurso,
            tipo_recurso,
            ubicacion,
            permiso,
            descripcion,
            activo,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, 1,
            datetime('now'),
            datetime('now')
        )
    """, (
        proyecto_id,
        nombre_recurso,
        tipo_recurso,
        ubicacion,
        permiso,
        descripcion
    ))

    conexion.commit()
    conexion.close()


def obtener_accesos(proyecto_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            nombre_recurso,
            tipo_recurso,
            ubicacion,
            permiso,
            descripcion,
            activo,
            fecha_creacion,
            fecha_actualizacion
        FROM accesos_proyecto
        WHERE proyecto_id = ?
        ORDER BY id
    """, (proyecto_id,))

    accesos = cursor.fetchall()

    conexion.close()

    return accesos


def actualizar_acceso(
    acceso_id,
    nombre_recurso,
    tipo_recurso,
    ubicacion,
    permiso,
    descripcion
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE accesos_proyecto
        SET
            nombre_recurso = ?,
            tipo_recurso = ?,
            ubicacion = ?,
            permiso = ?,
            descripcion = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        nombre_recurso,
        tipo_recurso,
        ubicacion,
        permiso,
        descripcion,
        acceso_id
    ))

    conexion.commit()
    conexion.close()


def cambiar_estado_acceso(acceso_id, activo):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE accesos_proyecto
        SET
            activo = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        activo,
        acceso_id
    ))

    conexion.commit()
    conexion.close()


def guardar_flujo(
    proyecto_id,
    nombre,
    descripcion,
    disparador,
    condicion,
    accion,
    prioridad=0
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO flujos_proyecto (
            proyecto_id,
            nombre,
            descripcion,
            disparador,
            condicion,
            accion,
            prioridad,
            activo,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, 1,
            datetime('now'),
            datetime('now')
        )
    """, (
        proyecto_id,
        nombre,
        descripcion,
        disparador,
        condicion,
        accion,
        prioridad
    ))

    conexion.commit()
    conexion.close()


def obtener_flujos(proyecto_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            nombre,
            descripcion,
            disparador,
            condicion,
            accion,
            prioridad,
            activo,
            fecha_creacion,
            fecha_actualizacion
        FROM flujos_proyecto
        WHERE proyecto_id = ?
        ORDER BY prioridad DESC, id
    """, (proyecto_id,))

    flujos = cursor.fetchall()

    conexion.close()

    return flujos


def actualizar_flujo(
    flujo_id,
    nombre,
    descripcion,
    disparador,
    condicion,
    accion,
    prioridad
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE flujos_proyecto
        SET
            nombre = ?,
            descripcion = ?,
            disparador = ?,
            condicion = ?,
            accion = ?,
            prioridad = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        nombre,
        descripcion,
        disparador,
        condicion,
        accion,
        prioridad,
        flujo_id
    ))

    conexion.commit()
    conexion.close()


def cambiar_estado_flujo(flujo_id, activo):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE flujos_proyecto
        SET
            activo = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        activo,
        flujo_id
    ))

    conexion.commit()
    conexion.close()


def guardar_funcion(
    nombre,
    categoria,
    descripcion,
    objetivo,
    estrategia_resolucion,
    derivacion_humana=True,
    activa=True
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO funciones_catalogo (
            nombre,
            categoria,
            descripcion,
            objetivo,
            estrategia_resolucion,
            derivacion_humana,
            activa,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, 
            datetime('now'),
            datetime('now')
        )
    """, (
        nombre,
        categoria,
        descripcion,
        objetivo,
        estrategia_resolucion,
        1 if derivacion_humana else 0,
        1 if activa else 0
    ))

    conexion.commit()
    conexion.close()


def obtener_funciones():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            categoria,
            descripcion,
            objetivo,
            estrategia_resolucion,
            derivacion_humana,
            activa,
            fecha_creacion,
            fecha_actualizacion
        FROM funciones_catalogo
        ORDER BY categoria, nombre
    """)

    funciones = cursor.fetchall()

    conexion.close()

    return funciones


def obtener_funcion(funcion_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            categoria,
            descripcion,
            objetivo,
            estrategia_resolucion,
            derivacion_humana,
            activa,
            fecha_creacion,
            fecha_actualizacion
        FROM funciones_catalogo
        WHERE id = ?
    """, (funcion_id,))

    funcion = cursor.fetchone()

    conexion.close()

    return funcion


# =========================================================
# ESTACIÓN 12 — NIVEL 1
# GESTIÓN DE INTENCIONES
# =========================================================


def crear_intencion(
    nombre,
    codigo,
    descripcion=None,
    categoria=None,
    prioridad=0,
    requiere_contexto=0,
    permite_derivacion=1,
    activa=1
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO intenciones (
            nombre,
            codigo,
            descripcion,
            categoria,
            prioridad,
            requiere_contexto,
            permite_derivacion,
            activa,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        nombre,
        codigo,
        descripcion,
        categoria,
        prioridad,
        requiere_contexto,
        permite_derivacion,
        activa
    ))

    intencion_id = cursor.lastrowid

    conexion.commit()
    conexion.close()

    return intencion_id


def obtener_intenciones():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            codigo,
            descripcion,
            categoria,
            prioridad,
            requiere_contexto,
            permite_derivacion,
            activa,
            fecha_creacion,
            fecha_actualizacion
        FROM intenciones
        ORDER BY categoria, prioridad DESC, nombre
    """)

    intenciones = cursor.fetchall()

    conexion.close()

    return intenciones


def obtener_intencion(intencion_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            codigo,
            descripcion,
            categoria,
            prioridad,
            requiere_contexto,
            permite_derivacion,
            activa,
            fecha_creacion,
            fecha_actualizacion
        FROM intenciones
        WHERE id = ?
    """, (intencion_id,))

    intencion = cursor.fetchone()

    conexion.close()

    return intencion


def actualizar_intencion(
    intencion_id,
    nombre,
    codigo,
    descripcion,
    categoria,
    prioridad,
    requiere_contexto,
    permite_derivacion,
    activa
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE intenciones
        SET
            nombre = ?,
            codigo = ?,
            descripcion = ?,
            categoria = ?,
            prioridad = ?,
            requiere_contexto = ?,
            permite_derivacion = ?,
            activa = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        nombre,
        codigo,
        descripcion,
        categoria,
        prioridad,
        requiere_contexto,
        permite_derivacion,
        activa,
        intencion_id
    ))

    conexion.commit()
    conexion.close()


def eliminar_intencion(intencion_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM patrones_intencion
        WHERE intencion_id = ?
    """, (intencion_id,))

    cursor.execute("""
        DELETE FROM intenciones_proyecto
        WHERE intencion_id = ?
    """, (intencion_id,))

    cursor.execute("""
        DELETE FROM intenciones
        WHERE id = ?
    """, (intencion_id,))

    conexion.commit()
    conexion.close()


def guardar_requisito_intencion(
    intencion_id,
    codigo,
    nombre,
    tipo="texto",
    obligatorio=True,
    prioridad=0,
    descripcion=None,
    activo=True
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO requisitos_intencion (
            intencion_id,
            codigo,
            nombre,
            tipo,
            obligatorio,
            prioridad,
            descripcion,
            activo,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        intencion_id,
        codigo,
        nombre,
        tipo,
        1 if obligatorio else 0,
        prioridad,
        descripcion,
        1 if activo else 0
    ))

    conexion.commit()
    conexion.close()


def obtener_requisitos_intencion(
    intencion_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            intencion_id,
            codigo,
            nombre,
            tipo,
            obligatorio,
            prioridad,
            descripcion,
            activo,
            fecha_creacion,
            fecha_actualizacion
        FROM requisitos_intencion
        WHERE intencion_id = ?
        ORDER BY prioridad DESC, nombre
    """, (
        intencion_id,
    ))

    requisitos = cursor.fetchall()

    conexion.close()

    return requisitos


def obtener_requisito_intencion(
    requisito_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            intencion_id,
            codigo,
            nombre,
            tipo,
            obligatorio,
            prioridad,
            descripcion,
            activo,
            fecha_creacion,
            fecha_actualizacion
        FROM requisitos_intencion
        WHERE id = ?
    """, (
        requisito_id,
    ))

    requisito = cursor.fetchone()

    conexion.close()

    return requisito


def actualizar_requisito_intencion(
    requisito_id,
    codigo,
    nombre,
    tipo,
    obligatorio,
    prioridad,
    descripcion,
    activo
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE requisitos_intencion
        SET
            codigo = ?,
            nombre = ?,
            tipo = ?,
            obligatorio = ?,
            prioridad = ?,
            descripcion = ?,
            activo = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        codigo,
        nombre,
        tipo,
        1 if obligatorio else 0,
        prioridad,
        descripcion,
        1 if activo else 0,
        requisito_id
    ))

    conexion.commit()
    conexion.close()


def cambiar_estado_requisito_intencion(
    requisito_id,
    activo
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE requisitos_intencion
        SET
            activo = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        1 if activo else 0,
        requisito_id
    ))

    conexion.commit()
    conexion.close()


def eliminar_requisito_intencion(
    requisito_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM requisitos_intencion
        WHERE id = ?
    """, (
        requisito_id,
    ))

    conexion.commit()
    conexion.close()
    

def actualizar_funcion(
    funcion_id,
    nombre,
    categoria,
    descripcion,
    objetivo,
    estrategia_resolucion,
    derivacion_humana,
    activa
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE funciones_catalogo
        SET
            nombre = ?,
            categoria = ?,
            descripcion = ?,
            objetivo = ?,
            estrategia_resolucion = ?,
            derivacion_humana = ?,
            activa = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        nombre,
        categoria,
        descripcion,
        objetivo,
        estrategia_resolucion,
        1 if derivacion_humana else 0,
        1 if activa else 0,
        funcion_id
    ))

    conexion.commit()
    conexion.close()


def cambiar_estado_funcion(funcion_id, activa):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE funciones_catalogo
        SET
            activa = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        1 if activa else 0,
        funcion_id
    ))

    conexion.commit()
    conexion.close()


def asignar_funcion_proyecto(
    proyecto_id,
    funcion_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO funciones_proyecto (
            proyecto_id,
            funcion_id,
            activa,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, 1,
            datetime('now'),
            datetime('now')
        )
    """, (
        proyecto_id,
        funcion_id
    ))

    conexion.commit()
    conexion.close()


def obtener_funciones_proyecto(
    proyecto_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            fp.id,
            fp.proyecto_id,
            fp.funcion_id,
            fc.nombre,
            fc.categoria,
            fc.descripcion,
            fc.objetivo,
            fc.estrategia_resolucion,
            fc.derivacion_humana,
            fp.activa
        FROM funciones_proyecto fp

        INNER JOIN funciones_catalogo fc
            ON fp.funcion_id = fc.id

        WHERE fp.proyecto_id = ?

        ORDER BY fc.categoria, fc.nombre
    """, (
        proyecto_id,
    ))

    funciones = cursor.fetchall()

    conexion.close()

    return funciones


# =========================================================
# ESTACIÓN 12 — NIVEL 1
# INTENCIONES DEL PROYECTO
# =========================================================


def agregar_intencion_proyecto(
    proyecto_id,
    intencion_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO intenciones_proyecto (
            proyecto_id,
            intencion_id,
            activa,
            prioridad,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, 1, 0,
            datetime('now'),
            datetime('now')
        )
    """, (
        proyecto_id,
        intencion_id
    ))

    conexion.commit()
    conexion.close()


def obtener_intenciones_proyecto(
    proyecto_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            ip.id,
            ip.proyecto_id,
            ip.intencion_id,

            i.nombre,
            i.codigo,
            i.descripcion,
            i.categoria,

            ip.prioridad,

            i.requiere_contexto,
            i.permite_derivacion,

            ip.activa

        FROM intenciones_proyecto ip

        INNER JOIN intenciones i
            ON ip.intencion_id = i.id

        WHERE ip.proyecto_id = ?

        ORDER BY
            ip.prioridad DESC,
            i.categoria,
            i.nombre
    """, (
        proyecto_id,
    ))

    intenciones = cursor.fetchall()

    conexion.close()

    return intenciones


def obtener_intenciones_disponibles(
    proyecto_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            codigo,
            descripcion,
            categoria,
            prioridad,
            requiere_contexto,
            permite_derivacion,
            activa

        FROM intenciones

        WHERE id NOT IN (
            SELECT intencion_id
            FROM intenciones_proyecto
            WHERE proyecto_id = ?
        )

        AND activa = 1

        ORDER BY
            categoria,
            nombre
    """, (
        proyecto_id,
    ))

    intenciones = cursor.fetchall()

    conexion.close()

    return intenciones


def cambiar_estado_intencion_proyecto(
    proyecto_id,
    intencion_id,
    activa
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE intenciones_proyecto

        SET
            activa = ?,
            fecha_actualizacion = datetime('now')

        WHERE proyecto_id = ?
        AND intencion_id = ?
    """, (
        activa,
        proyecto_id,
        intencion_id
    ))

    conexion.commit()
    conexion.close()


def actualizar_prioridad_intencion_proyecto(
    proyecto_id,
    intencion_id,
    prioridad
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE intenciones_proyecto

        SET
            prioridad = ?,
            fecha_actualizacion = datetime('now')

        WHERE proyecto_id = ?
        AND intencion_id = ?
    """, (
        prioridad,
        proyecto_id,
        intencion_id
    ))

    conexion.commit()
    conexion.close()


def quitar_intencion_proyecto(
    proyecto_id,
    intencion_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM intenciones_proyecto

        WHERE proyecto_id = ?
        AND intencion_id = ?
    """, (
        proyecto_id,
        intencion_id
    ))

    conexion.commit()
    conexion.close()


def obtener_funciones_disponibles_para_proyecto(
    proyecto_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            fc.id,
            fc.nombre,
            fc.categoria,
            fc.descripcion,
            fc.objetivo,
            fc.estrategia_resolucion,
            fc.derivacion_humana,
            fc.activa
        FROM funciones_catalogo fc

        WHERE fc.activa = 1

        AND fc.id NOT IN (
            SELECT funcion_id
            FROM funciones_proyecto
            WHERE proyecto_id = ?
        )

        ORDER BY fc.categoria, fc.nombre
    """, (
        proyecto_id,
    ))

    funciones = cursor.fetchall()

    conexion.close()

    return funciones


def cambiar_estado_funcion_proyecto(
    relacion_id,
    activa
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE funciones_proyecto
        SET
            activa = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        1 if activa else 0,
        relacion_id
    ))

    conexion.commit()
    conexion.close()


def quitar_funcion_proyecto(
    relacion_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM funciones_proyecto
        WHERE id = ?
    """, (
        relacion_id,
    ))

    conexion.commit()
    conexion.close()


def guardar_herramienta_proyecto(
    proyecto_id,
    nombre,
    tipo,
    descripcion,
    configuracion=""
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO herramientas_proyecto (
            proyecto_id,
            nombre,
            tipo,
            descripcion,
            configuracion,
            activo,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, ?, ?, ?, 1,
            datetime('now'),
            datetime('now')
        )
    """, (
        proyecto_id,
        nombre,
        tipo,
        descripcion,
        configuracion
    ))

    conexion.commit()
    conexion.close()


def obtener_herramientas_proyecto(proyecto_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            tipo,
            descripcion,
            configuracion,
            activo
        FROM herramientas_proyecto
        WHERE proyecto_id = ?
        ORDER BY nombre
    """, (proyecto_id,))

    herramientas = cursor.fetchall()

    conexion.close()

    return herramientas


def obtener_herramienta_por_id(herramienta_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            proyecto_id,
            nombre,
            tipo,
            descripcion,
            configuracion,
            activo
        FROM herramientas_proyecto
        WHERE id = ?
    """, (herramienta_id,))

    herramienta = cursor.fetchone()

    conexion.close()

    return herramienta

def cambiar_estado_herramienta(
    herramienta_id,
    activa
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE herramientas_proyecto
        SET
            activo = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        1 if activa else 0,
        herramienta_id
    ))

    conexion.commit()
    conexion.close()

def eliminar_herramienta_proyecto(herramienta_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM herramientas_proyecto
        WHERE id = ?
    """, (herramienta_id,))

    conexion.commit()
    conexion.close()


def guardar_accion_herramienta(
    herramienta_id,
    nombre,
    operacion,
    descripcion="",
    parametros=""
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO acciones_herramienta (
            herramienta_id,
            nombre,
            descripcion,
            operacion,
            parametros,
            activo,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, ?, ?, ?, 1,
            datetime('now'),
            datetime('now')
        )
    """, (
        herramienta_id,
        nombre,
        descripcion,
        operacion,
        parametros
    ))

    conexion.commit()
    conexion.close()

def obtener_acciones_herramienta(herramienta_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            operacion,
            descripcion,
            parametros,
            activo
        FROM acciones_herramienta
        WHERE herramienta_id = ?
        ORDER BY nombre
    """, (herramienta_id,))

    acciones = cursor.fetchall()

    conexion.close()

    return acciones

def obtener_accion_por_id(accion_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            herramienta_id,
            nombre,
            operacion,
            descripcion,
            parametros,
            activo
        FROM acciones_herramienta
        WHERE id = ?
    """, (accion_id,))

    accion = cursor.fetchone()

    conexion.close()

    return accion


def obtener_accion_herramienta(accion_id):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            herramienta_id,
            nombre,
            descripcion,
            operacion,
            parametros,
            activo,
            fecha_creacion,
            fecha_actualizacion
        FROM acciones_herramienta
        WHERE id = ?
    """, (accion_id,))

    resultado = cursor.fetchone()

    conexion.close()

    return resultado

def cambiar_estado_accion(
    accion_id,
    activa
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE acciones_herramienta
        SET
            activo = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        1 if activa else 0,
        accion_id
    ))

    conexion.commit()
    conexion.close()


def eliminar_accion_herramienta(accion_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM acciones_herramienta
        WHERE id = ?
    """, (accion_id,))

    conexion.commit()
    conexion.close()


def asignar_accion_a_funcion(
    funcion_id,
    accion_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO funciones_acciones (
            funcion_id,
            accion_id,
            activa,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, 1,
            datetime('now'),
            datetime('now')
        )
    """, (
        funcion_id,
        accion_id
    ))

    conexion.commit()
    conexion.close()


def obtener_acciones_de_funcion(funcion_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            fa.id,
            ah.id,
            ah.nombre,
            ah.operacion,
            ah.descripcion,
            fa.activa
        FROM funciones_acciones fa
        INNER JOIN acciones_herramienta ah
            ON ah.id = fa.accion_id
        WHERE fa.funcion_id = ?
        ORDER BY ah.nombre
    """, (funcion_id,))

    acciones = cursor.fetchall()

    conexion.close()

    return acciones


def cambiar_estado_accion_funcion(
    relacion_id,
    activa
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE funciones_acciones
        SET
            activa = ?,
            fecha_actualizacion = datetime('now')
        WHERE id = ?
    """, (
        1 if activa else 0,
        relacion_id
    ))

    conexion.commit()
    conexion.close()


def quitar_accion_de_funcion(relacion_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM funciones_acciones
        WHERE id = ?
    """, (relacion_id,))

    conexion.commit()
    conexion.close()


def obtener_acciones_disponibles_para_funcion(funcion_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            ah.id,
            ah.nombre,
            ah.operacion,
            ah.descripcion,
            ah.activo
        FROM acciones_herramienta ah
        INNER JOIN herramientas_proyecto hp
            ON hp.id = ah.herramienta_id
        WHERE ah.activo = 1
        AND hp.activo = 1
        AND hp.proyecto_id = (
            SELECT proyecto_id
            FROM funciones_proyecto
            WHERE funcion_id = ?
            LIMIT 1
        )
        AND ah.id NOT IN (
            SELECT accion_id
            FROM funciones_acciones
            WHERE funcion_id = ?
        )
        ORDER BY ah.nombre
    """, (
        funcion_id,
        funcion_id
    ))

    acciones = cursor.fetchall()

    conexion.close()

    return acciones


def obtener_capacidades_funcion(funcion_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            fa.funcion_id,

            ah.id AS accion_id,
            ah.nombre AS accion_nombre,
            ah.operacion,
            ah.descripcion AS accion_descripcion,

            hp.id AS herramienta_id,
            hp.nombre AS herramienta_nombre,
            hp.tipo AS herramienta_tipo,
            hp.proveedor,

            fa.activa AS relacion_activa,
            ah.activo AS accion_activa,
            hp.activo AS herramienta_activa

        FROM funciones_acciones fa

        INNER JOIN acciones_herramienta ah
            ON ah.id = fa.accion_id

        INNER JOIN herramientas_proyecto hp
            ON hp.id = ah.herramienta_id

        WHERE fa.funcion_id = ?

        AND fa.activa = 1
        AND ah.activo = 1
        AND hp.activo = 1

        ORDER BY
            hp.nombre,
            ah.nombre

    """, (funcion_id,))

    capacidades = cursor.fetchall()

    conexion.close()

    return capacidades


def obtener_capacidades_proyecto(proyecto_id):

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            fp.funcion_id,
            f.nombre AS funcion_nombre,

            ah.id AS accion_id,
            ah.nombre AS accion_nombre,
            ah.operacion,
            ah.descripcion AS accion_descripcion,

            hp.id AS herramienta_id,
            hp.nombre AS herramienta_nombre,
            hp.tipo AS herramienta_tipo,
            hp.proveedor

        FROM funciones_proyecto fp

        INNER JOIN funciones_catalogo f
            ON f.id = fp.funcion_id

        INNER JOIN funciones_acciones fa
            ON fa.funcion_id = fp.funcion_id

        INNER JOIN acciones_herramienta ah
            ON ah.id = fa.accion_id

        INNER JOIN herramientas_proyecto hp
            ON hp.id = ah.herramienta_id

        WHERE fp.proyecto_id = ?

        AND fp.activa = 1
        AND fa.activa = 1
        AND ah.activo = 1
        AND hp.activo = 1

        ORDER BY
            f.nombre,
            hp.nombre,
            ah.nombre

    """, (proyecto_id,))

    capacidades = cursor.fetchall()

    conexion.close()

    return capacidades

crear_base() 


# =========================================================
# ESTACIÓN 12 — NIVEL 1
# PATRONES DE INTENCIÓN
# =========================================================


def crear_patron_intencion(
    intencion_id,
    patron,
    tipo="FRASE",
    prioridad=0,
    activo=True
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO patrones_intencion (
            intencion_id,
            patron,
            tipo,
            prioridad,
            activo,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (
            ?, ?, ?, ?, ?,
            datetime('now'),
            datetime('now')
        )
    """, (
        intencion_id,
        patron,
        tipo,
        prioridad,
        1 if activo else 0
    ))

    conexion.commit()
    conexion.close()


def obtener_patrones_intencion(
    intencion_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            intencion_id,
            patron,
            tipo,
            prioridad,
            activo,
            fecha_creacion,
            fecha_actualizacion

        FROM patrones_intencion

        WHERE intencion_id = ?

        ORDER BY
            prioridad DESC,
            patron
    """, (
        intencion_id,
    ))

    patrones = cursor.fetchall()

    conexion.close()

    return patrones


def obtener_patron_intencion(
    patron_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            intencion_id,
            patron,
            tipo,
            prioridad,
            activo,
            fecha_creacion,
            fecha_actualizacion

        FROM patrones_intencion

        WHERE id = ?
    """, (
        patron_id,
    ))

    patron = cursor.fetchone()

    conexion.close()

    return patron


def actualizar_patron_intencion(
    patron_id,
    patron,
    tipo,
    prioridad,
    activo
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE patrones_intencion

        SET
            patron = ?,
            tipo = ?,
            prioridad = ?,
            activo = ?,
            fecha_actualizacion = datetime('now')

        WHERE id = ?
    """, (
        patron,
        tipo,
        prioridad,
        1 if activo else 0,
        patron_id
    ))

    conexion.commit()
    conexion.close()


def eliminar_patron_intencion(
    patron_id
):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM patrones_intencion

        WHERE id = ?
    """, (
        patron_id,
    ))

    conexion.commit()
    conexion.close()
