ESTADO_APROBADO = "APROBADO"
ESTADO_FALLIDO = "FALLIDO"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_ERROR = "ERROR"


def _contenido(valor):
    return bool(valor.strip()) if isinstance(valor, str) else bool(valor)


def _buscar(datos, *claves):
    for clave in claves:
        valor = datos.get(clave) if isinstance(datos, dict) else None
        if _contenido(valor):
            return valor
    return None


def _prueba(nombre, valor, requerido=True):
    if _contenido(valor):
        return {"estado": ESTADO_APROBADO, "cantidad": len(valor) if isinstance(valor, (list, dict)) else 1, "detalles": [f"{nombre} disponible."]}
    return {"estado": ESTADO_FALLIDO if requerido else ESTADO_INCOMPLETO, "cantidad": 0, "detalles": [f"No hay {nombre.lower()} utilizable."]}


def probar_conocimiento(paquete_pruebas):
    """Comprueba los datos reales entregados por 14.1, sin inventarlos."""
    resultado = {"estacion": 14, "nivel": "14.2", "nombre": "Prueba de conocimiento", "estado": ESTADO_ERROR,
                 "pruebas": {}, "resumen": {}, "errores": [], "advertencias": []}
    if not isinstance(paquete_pruebas, dict) or paquete_pruebas.get("estado_preparacion") != "PREPARADO":
        resultado["errores"].append("El paquete de 14.1 no está preparado.")
        return resultado
    datos = paquete_pruebas.get("datos", {})
    configuracion, cerebro, personalidad = datos.get("configuracion", {}), datos.get("cerebro", {}), datos.get("personalidad", {})
    identidad = _buscar(configuracion, "identidad", "asistente", "empresa", "proyecto")
    bloque_conocimiento = configuracion.get("conocimiento", {})
    catalogo = _buscar(bloque_conocimiento, "catalogo", "productos", "servicios")
    conocimiento = _buscar(bloque_conocimiento, "conocimiento_general", "base_conocimiento") or _buscar(cerebro, "conocimiento", "base_conocimiento")
    ia = _buscar(configuracion, "configuracion_ia", "ia") or _buscar(personalidad, "configuracion_ia", "modelo")
    resultado["pruebas"] = {"identidad": _prueba("Identidad", identidad), "catalogo": _prueba("Catálogo", catalogo, False),
                            "conocimiento": _prueba("Conocimiento general", conocimiento, False), "configuracion_ia": _prueba("Configuración de IA", ia)}
    estados = [p["estado"] for p in resultado["pruebas"].values()]
    resultado["resumen"] = {"pruebas_totales": len(estados), "pruebas_aprobadas": estados.count(ESTADO_APROBADO), "pruebas_fallidas": estados.count(ESTADO_FALLIDO), "pruebas_incompletas": estados.count(ESTADO_INCOMPLETO)}
    resultado["estado"] = ESTADO_FALLIDO if ESTADO_FALLIDO in estados else ESTADO_INCOMPLETO if ESTADO_INCOMPLETO in estados else ESTADO_APROBADO
    resultado["advertencias"] = [f"{n} está incompleta." for n, p in resultado["pruebas"].items() if p["estado"] == ESTADO_INCOMPLETO]
    return resultado


def obtener_resumen_conocimiento(resultado):
    if not isinstance(resultado, dict):
        return {"estacion": 14, "nivel": "14.2", "estado": ESTADO_ERROR}
    return {"estacion": 14, "nivel": "14.2", "estado": resultado.get("estado", ESTADO_ERROR), "resumen": resultado.get("resumen", {}), "pruebas": resultado.get("pruebas", {}), "errores": resultado.get("errores", []), "advertencias": resultado.get("advertencias", [])}
