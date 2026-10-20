import json
import os

from db_manager import obtener_asistente


ESTADO_PREPARADO = "PREPARADO"
ESTADO_BLOQUEADO = "BLOQUEADO"
ESTADO_ERROR = "ERROR"

ESTADO_ASISTENTE_VALIDO = "Listo para pruebas"
ESTADO_ACTIVACION_VALIDO = "LISTO_PARA_PRUEBAS"


ARCHIVOS_REQUERIDOS = [
    "configuracion.json",
    "cerebro.json",
    "personalidad.json",
    "metadatos.json",
    "asistente.py",
    "activacion.json",
]


def crear_preparacion_base():
    """
    Crea la estructura base de una preparación de pruebas.
    """

    return {
        "estacion": 14,
        "nivel": "14.1",
        "nombre": "Preparación de la prueba",
        "estado": ESTADO_BLOQUEADO,
        "asistente_id": None,
        "ruta_asistente": None,
        "listo_para_pruebas": False,
        "archivos_validos": False,
        "json_validos": False,
        "componentes": {
            "configuracion": False,
            "cerebro": False,
            "personalidad": False,
            "metadatos": False,
            "runtime": False,
            "activacion": False,
        },
        "datos": {
            "configuracion": None,
            "cerebro": None,
            "personalidad": None,
            "metadatos": None,
            "activacion": None,
        },
        "errores": [],
        "advertencias": [],
    }


def obtener_ruta_asistente(asistente):
    """
    Obtiene la carpeta donde fue generado el asistente.

    La Estación 13 guarda la ruta del asistente dentro
    del campo configuracion del registro de asistentes.
    """

    if not asistente:
        return None

    configuracion = asistente[4]

    if not configuracion:
        return None

    try:
        if isinstance(configuracion, str):
            configuracion = json.loads(configuracion)

        if not isinstance(configuracion, dict):
            return None

        rutas = configuracion.get("rutas", {})

        if isinstance(rutas, dict):
            for clave in [
                "directorio",
                "ruta_asistente",
                "carpeta",
            ]:
                ruta = rutas.get(clave)

                if ruta:
                    return os.path.abspath(ruta)

        for clave in [
            "directorio",
            "ruta_asistente",
            "carpeta",
        ]:
            ruta = configuracion.get(clave)

            if ruta:
                return os.path.abspath(ruta)

    except Exception:
        return None

    return None


def buscar_ruta_desde_archivo(asistente):
    """
    Intenta recuperar la carpeta del asistente utilizando
    las rutas almacenadas en los archivos de configuración.
    """

    if not asistente:
        return None

    configuracion = asistente[4]

    if not configuracion:
        return None

    try:
        if isinstance(configuracion, str):
            configuracion = json.loads(configuracion)

        rutas = configuracion.get("rutas", {})

        posibles_rutas = []

        if isinstance(rutas, dict):
            posibles_rutas.extend(
                rutas.values()
            )

        posibles_rutas.extend([
            configuracion.get("configuracion"),
            configuracion.get("ruta_configuracion"),
        ])

        for valor in posibles_rutas:

            if not valor:
                continue

            ruta = os.path.abspath(str(valor))

            if os.path.isfile(ruta):
                return os.path.dirname(ruta)

    except Exception:
        return None

    return None


def cargar_json(ruta):
    """
    Carga un archivo JSON y devuelve:
    (exito, contenido, error)
    """

    if not os.path.isfile(ruta):
        return (
            False,
            None,
            f"No existe el archivo: {ruta}",
        )

    try:
        with open(
            ruta,
            "r",
            encoding="utf-8",
        ) as archivo:

            contenido = json.load(archivo)

        if not isinstance(contenido, dict):
            return (
                False,
                None,
                f"El archivo no contiene un objeto JSON válido: {ruta}",
            )

        return True, contenido, None

    except json.JSONDecodeError as error:
        return (
            False,
            None,
            f"JSON inválido en {ruta}: {error}",
        )

    except Exception as error:
        return (
            False,
            None,
            f"Error leyendo {ruta}: {error}",
        )


def validar_archivos(preparacion, ruta_asistente):
    """
    Comprueba que existan los archivos generados
    por la Estación 13.
    """

    archivos = {}

    for nombre in ARCHIVOS_REQUERIDOS:

        ruta = os.path.join(
            ruta_asistente,
            nombre,
        )

        existe = os.path.isfile(ruta)

        archivos[nombre] = existe

        if not existe:
            preparacion["errores"].append(
                f"Falta el archivo requerido: {nombre}"
            )

    preparacion["componentes"]["configuracion"] = archivos[
        "configuracion.json"
    ]

    preparacion["componentes"]["cerebro"] = archivos[
        "cerebro.json"
    ]

    preparacion["componentes"]["personalidad"] = archivos[
        "personalidad.json"
    ]

    preparacion["componentes"]["metadatos"] = archivos[
        "metadatos.json"
    ]

    preparacion["componentes"]["runtime"] = archivos[
        "asistente.py"
    ]

    preparacion["componentes"]["activacion"] = archivos[
        "activacion.json"
    ]

    preparacion["archivos_validos"] = (
        len(preparacion["errores"]) == 0
    )

    return preparacion


def cargar_componentes(preparacion, ruta_asistente):
    """
    Carga los JSON necesarios para las pruebas posteriores.
    """

    nombres = {
        "configuracion": "configuracion.json",
        "cerebro": "cerebro.json",
        "personalidad": "personalidad.json",
        "metadatos": "metadatos.json",
        "activacion": "activacion.json",
    }

    todos_validos = True

    for clave, nombre in nombres.items():

        ruta = os.path.join(
            ruta_asistente,
            nombre,
        )

        exito, contenido, error = cargar_json(ruta)

        if exito:

            preparacion["datos"][clave] = contenido

        else:

            todos_validos = False

            preparacion["errores"].append(error)

    preparacion["json_validos"] = todos_validos

    return preparacion


def validar_activacion(preparacion):
    """
    Comprueba que la activación producida por la
    Estación 13 permita comenzar las pruebas.
    """

    activacion = preparacion["datos"]["activacion"]

    if not activacion:
        preparacion["errores"].append(
            "No se pudo cargar la activación del asistente."
        )
        return preparacion

    estado = activacion.get("estado")

    activo = activacion.get("activo")

    listo = activacion.get("listo_para_pruebas")

    if estado != ESTADO_ACTIVACION_VALIDO:

        preparacion["errores"].append(
            "La activación no está en estado "
            f"{ESTADO_ACTIVACION_VALIDO}."
        )

    if activo is not True:

        preparacion["errores"].append(
            "El asistente no figura como activo."
        )

    if listo is not True:

        preparacion["errores"].append(
            "La activación no indica que el asistente "
            "está listo para pruebas."
        )

    return preparacion


def validar_estructuras(preparacion):
    """
    Comprueba que los componentes principales tengan
    estructuras utilizables por los niveles posteriores.
    """

    configuracion = preparacion["datos"]["configuracion"]
    cerebro = preparacion["datos"]["cerebro"]
    personalidad = preparacion["datos"]["personalidad"]
    metadatos = preparacion["datos"]["metadatos"]

    if not isinstance(configuracion, dict):
        preparacion["errores"].append(
            "La configuración del asistente no es válida."
        )

    if not isinstance(cerebro, dict):
        preparacion["errores"].append(
            "El cerebro del asistente no es válido."
        )

    if not isinstance(personalidad, dict):
        preparacion["errores"].append(
            "La personalidad del asistente no es válida."
        )

    if not isinstance(metadatos, dict):
        preparacion["errores"].append(
            "Los metadatos del asistente no son válidos."
        )

    return preparacion


def crear_paquete_pruebas(preparacion):
    """
    Crea el paquete común que utilizarán los niveles
    14.2, 14.3 y 14.4.
    """

    return {
        "estacion": 14,
        "asistente_id": preparacion["asistente_id"],
        "ruta_asistente": preparacion["ruta_asistente"],
        "estado_preparacion": preparacion["estado"],
        "componentes": preparacion["componentes"],
        "datos": preparacion["datos"],
        "resultados": {
            "14.2_conocimiento": None,
            "14.3_inteligencia": None,
            "14.4_conversacion": None,
            "14.5_validacion": None,
        },
    }


def preparar_prueba(proyecto_id):
    """
    Ejecuta completamente el nivel 14.1.

    No realiza pruebas de conocimiento, inteligencia
    ni conversación.

    Su única responsabilidad es dejar al asistente
    correctamente preparado para ser evaluado.
    """

    preparacion = crear_preparacion_base()

    try:

        asistente = obtener_asistente(proyecto_id)

        if not asistente:

            preparacion["errores"].append(
                "No existe un asistente asociado al proyecto."
            )

            preparacion["estado"] = ESTADO_BLOQUEADO

            return {
                "preparacion": preparacion,
                "paquete_pruebas": None,
            }

        asistente_id = asistente[0]

        nombre = asistente[2]

        estado_asistente = asistente[5]

        preparacion["asistente_id"] = (
            f"AST-{int(asistente_id):06d}"
            if isinstance(asistente_id, int)
            else str(asistente_id)
        )

        if estado_asistente != ESTADO_ASISTENTE_VALIDO:

            preparacion["errores"].append(
                "El asistente no está en estado "
                f"'{ESTADO_ASISTENTE_VALIDO}'. "
                f"Estado actual: '{estado_asistente}'."
            )

        ruta_asistente = obtener_ruta_asistente(
            asistente
        )

        if not ruta_asistente:
            ruta_asistente = buscar_ruta_desde_archivo(
                asistente
            )

        if not ruta_asistente:

            preparacion["errores"].append(
                "No se pudo determinar la carpeta "
                "del asistente generado."
            )

        else:

            preparacion["ruta_asistente"] = (
                ruta_asistente
            )

        if ruta_asistente:

            validar_archivos(
                preparacion,
                ruta_asistente,
            )

            if preparacion["archivos_validos"]:

                cargar_componentes(
                    preparacion,
                    ruta_asistente,
                )

                if preparacion["json_validos"]:

                    validar_activacion(
                        preparacion
                    )

                    validar_estructuras(
                        preparacion
                    )

        if not preparacion["errores"]:

            preparacion["estado"] = ESTADO_PREPARADO

            preparacion["listo_para_pruebas"] = True

        else:

            preparacion["estado"] = ESTADO_BLOQUEADO

            preparacion["listo_para_pruebas"] = False

        preparacion["nombre_asistente"] = nombre

        paquete = None

        if preparacion["listo_para_pruebas"]:

            paquete = crear_paquete_pruebas(
                preparacion
            )

        return {
            "preparacion": preparacion,
            "paquete_pruebas": paquete,
        }

    except Exception as error:

        preparacion["estado"] = ESTADO_ERROR

        preparacion["listo_para_pruebas"] = False

        preparacion["errores"].append(
            f"Error general durante la preparación: {error}"
        )

        return {
            "preparacion": preparacion,
            "paquete_pruebas": None,
        }


def esta_preparado(resultado):
    """
    Indica si 14.1 terminó correctamente.
    """

    if not resultado:
        return False

    preparacion = resultado.get(
        "preparacion",
        {},
    )

    return (
        preparacion.get("estado")
        == ESTADO_PREPARADO
        and
        preparacion.get("listo_para_pruebas")
        is True
    )


def obtener_resumen_preparacion(resultado):
    """
    Genera un resumen simple para la interfaz
    o para las etapas siguientes.
    """

    if not resultado:

        return {
            "estado": ESTADO_ERROR,
            "asistente_id": None,
            "listo_para_pruebas": False,
            "errores": [
                "No existe resultado de preparación."
            ],
        }

    preparacion = resultado.get(
        "preparacion",
        {},
    )

    return {
        "estacion": 14,
        "nivel": "14.1",
        "estado": preparacion.get(
            "estado"
        ),
        "asistente_id": preparacion.get(
            "asistente_id"
        ),
        "ruta_asistente": preparacion.get(
            "ruta_asistente"
        ),
        "listo_para_pruebas": preparacion.get(
            "listo_para_pruebas",
            False,
        ),
        "archivos_validos": preparacion.get(
            "archivos_validos",
            False,
        ),
        "json_validos": preparacion.get(
            "json_validos",
            False,
        ),
        "componentes": preparacion.get(
            "componentes",
            {},
        ),
        "errores": preparacion.get(
            "errores",
            [],
        ),
        "advertencias": preparacion.get(
            "advertencias",
            [],
        ),
    }