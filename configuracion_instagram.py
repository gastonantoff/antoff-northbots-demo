"""Configuración local y segura del conector de Instagram.

Los valores sensibles se leen del entorno del sistema. No deben guardarse
en el código, en la base de datos ni en archivos enviados al repositorio.
"""

import os


VARIABLES_REQUERIDAS = (
    "INSTAGRAM_APP_ID",
    "INSTAGRAM_APP_SECRET",
    "INSTAGRAM_ACCESS_TOKEN",
    "INSTAGRAM_IG_USER_ID",
    "INSTAGRAM_VERIFY_TOKEN",
)


def obtener_variable_entorno(nombre, predeterminado=""):
    """Lee una variable del proceso o de las Variables de usuario de Windows.

    VS Code no actualiza el entorno de terminales que ya estaban abiertas al
    crear una variable nueva. La segunda lectura evita reinicios innecesarios
    durante la configuración local y nunca muestra el valor obtenido.
    """
    valor = os.getenv(nombre, "").strip()

    if valor or os.name != "nt":
        return valor or predeterminado

    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as clave:
            valor, _ = winreg.QueryValueEx(clave, nombre)
            return str(valor).strip() or predeterminado
    except (FileNotFoundError, OSError):
        return predeterminado


def obtener_configuracion_instagram():
    """Obtiene la configuración actual sin exponer secretos en mensajes."""
    return {
        "app_id": obtener_variable_entorno("INSTAGRAM_APP_ID"),
        "app_secret": obtener_variable_entorno("INSTAGRAM_APP_SECRET"),
        "access_token": obtener_variable_entorno("INSTAGRAM_ACCESS_TOKEN"),
        "ig_user_id": obtener_variable_entorno("INSTAGRAM_IG_USER_ID"),
        "verify_token": obtener_variable_entorno("INSTAGRAM_VERIFY_TOKEN"),
        "graph_base_url": obtener_variable_entorno(
            "INSTAGRAM_GRAPH_BASE_URL",
            "https://graph.facebook.com",
        ).rstrip("/"),
        "graph_api_version": obtener_variable_entorno(
            "INSTAGRAM_GRAPH_API_VERSION",
        ),
    }


def obtener_faltantes_instagram(configuracion=None):
    """Devuelve sólo los nombres de las variables faltantes."""
    configuracion = configuracion or obtener_configuracion_instagram()

    mapa = {
        "INSTAGRAM_APP_ID": configuracion["app_id"],
        "INSTAGRAM_APP_SECRET": configuracion["app_secret"],
        "INSTAGRAM_ACCESS_TOKEN": configuracion["access_token"],
        "INSTAGRAM_IG_USER_ID": configuracion["ig_user_id"],
        "INSTAGRAM_VERIFY_TOKEN": configuracion["verify_token"],
    }

    return [
        variable
        for variable in VARIABLES_REQUERIDAS
        if not mapa[variable]
    ]


def configuracion_instagram_lista(configuracion=None):
    """Indica si existe la configuración mínima para el conector real."""
    return not obtener_faltantes_instagram(configuracion)
