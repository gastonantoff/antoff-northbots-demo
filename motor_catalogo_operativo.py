"""Catálogo operativo con fuentes externas controladas.

Este motor sirve para cualquier tipo de laboratorio. Trata únicamente
información comercial y operativa publicada: prestaciones, servicios,
insumos, precios, requisitos, vigencia y disponibilidad. Nunca procesa
resultados, historias clínicas ni datos identificatorios de pacientes.
"""

from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
from datetime import datetime, timezone


CAMPOS_CATALOGO = (
    "codigo",
    "nombre",
    "categoria",
    "descripcion",
    "precio",
    "estado",
    "condiciones",
    "vigencia",
)

TERMINOS_SENSIBLES = (
    "paciente",
    "dni",
    "documento",
    "historia_clinica",
    "resultado",
    "diagnostico",
    "muestra_biologica",
)


def normalizar_texto(valor):
    texto = unicodedata.normalize("NFD", str(valor or "").lower())
    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_precio(valor):
    if valor in (None, ""):
        return None

    texto = str(valor).strip().replace("$", "").replace(".", "")
    texto = texto.replace(",", ".")

    try:
        return round(float(texto), 2)
    except ValueError as error:
        raise ValueError("El precio debe ser numérico.") from error


def normalizar_item(origen):
    """Convierte un registro de cualquier fuente al contrato común."""
    if not isinstance(origen, dict):
        raise ValueError("Cada registro de la fuente debe ser un objeto.")

    claves = {normalizar_texto(clave): valor for clave, valor in origen.items()}

    for clave in claves:
        if clave in TERMINOS_SENSIBLES:
            raise ValueError(
                "La fuente contiene un campo sensible no permitido: "
                f"{clave}."
            )

    item = {
        "codigo": str(claves.get("codigo", "")).strip(),
        "nombre": str(claves.get("nombre", "")).strip(),
        "categoria": str(claves.get("categoria", "General")).strip(),
        "descripcion": str(claves.get("descripcion", "")).strip(),
        "precio": normalizar_precio(claves.get("precio")),
        "estado": str(claves.get("estado", "ACTIVO")).strip().upper(),
        "condiciones": str(claves.get("condiciones", "")).strip(),
        "vigencia": str(claves.get("vigencia", "")).strip(),
    }

    if not item["codigo"]:
        raise ValueError("Cada registro debe incluir un código único.")

    if not item["nombre"]:
        raise ValueError(
            f"El registro {item['codigo']} no incluye un nombre."
        )

    return item


def normalizar_catalogo(registros):
    if not isinstance(registros, list):
        raise ValueError("La fuente debe entregar una lista de registros.")

    catalogo = []
    codigos = set()

    for registro in registros:
        item = normalizar_item(registro)
        codigo = normalizar_texto(item["codigo"])

        if codigo in codigos:
            raise ValueError(
                f"La fuente repite el código {item['codigo']}."
            )

        codigos.add(codigo)
        catalogo.append(item)

    return catalogo


def leer_csv_catalogo(contenido):
    """Lee un CSV UTF-8 con los encabezados del contrato de catálogo."""
    if not isinstance(contenido, str) or not contenido.strip():
        raise ValueError("La fuente CSV está vacía.")

    lector = csv.DictReader(io.StringIO(contenido))
    if not lector.fieldnames:
        raise ValueError("La fuente CSV no contiene encabezados.")

    return normalizar_catalogo(list(lector))


def leer_json_catalogo(contenido):
    """Lee una lista JSON de registros sin ejecutar instrucciones externas."""
    try:
        registros = json.loads(contenido)
    except json.JSONDecodeError as error:
        raise ValueError("La fuente JSON no es válida.") from error

    return normalizar_catalogo(registros)


def comparar_catalogos(publicado, candidato):
    """Calcula altas, cambios y bajas sin modificar el catálogo publicado."""
    publicado_por_codigo = {
        normalizar_texto(item["codigo"]): item
        for item in normalizar_catalogo(publicado)
    }
    candidato_por_codigo = {
        normalizar_texto(item["codigo"]): item
        for item in normalizar_catalogo(candidato)
    }

    altas = []
    cambios = []
    bajas = []

    for codigo, item in candidato_por_codigo.items():
        anterior = publicado_por_codigo.get(codigo)

        if anterior is None:
            altas.append(item)
            continue

        diferencias = {
            campo: {"anterior": anterior.get(campo), "nuevo": item.get(campo)}
            for campo in CAMPOS_CATALOGO
            if anterior.get(campo) != item.get(campo)
        }

        if diferencias:
            cambios.append({
                "codigo": item["codigo"],
                "diferencias": diferencias,
                "nuevo": item,
            })

    for codigo, item in publicado_por_codigo.items():
        if codigo not in candidato_por_codigo:
            bajas.append(item)

    return {
        "altas": altas,
        "cambios": cambios,
        "bajas": bajas,
        "sin_cambios": not (altas or cambios or bajas),
    }


def crear_revision_desde_fuente(publicado, candidato, fuente_nombre):
    """Genera una revisión pendiente; nunca publica automáticamente."""
    catalogo_candidato = normalizar_catalogo(candidato)
    diferencias = comparar_catalogos(publicado, catalogo_candidato)

    return {
        "estado": (
            "SIN_CAMBIOS"
            if diferencias["sin_cambios"]
            else "PENDIENTE_APROBACION"
        ),
        "fuente": str(fuente_nombre or "Fuente sin nombre"),
        "fecha_revision": datetime.now(timezone.utc).isoformat(),
        "resumen": {
            "altas": len(diferencias["altas"]),
            "cambios": len(diferencias["cambios"]),
            "bajas": len(diferencias["bajas"]),
        },
        "diferencias": diferencias,
        "catalogo_candidato": catalogo_candidato,
        "requiere_aprobacion_humana": True,
        "datos_sensibles_permitidos": False,
    }


def aprobar_revision(revision, aprobador):
    """Autoriza una revisión ya generada para que otro módulo la publique."""
    if revision.get("estado") != "PENDIENTE_APROBACION":
        raise ValueError("Solo se pueden aprobar revisiones pendientes.")

    if not str(aprobador or "").strip():
        raise ValueError("Debe identificarse la persona que aprueba.")

    aprobada = dict(revision)
    aprobada["estado"] = "APROBADA_PARA_PUBLICAR"
    aprobada["aprobada_por"] = str(aprobador).strip()
    aprobada["fecha_aprobacion"] = datetime.now(timezone.utc).isoformat()
    return aprobada
