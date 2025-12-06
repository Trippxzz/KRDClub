from .models import Configuracion
import json


def anuncios_context(request):
    """
    Context processor que carga los anuncios activos para mostrar en el banner.
    Los anuncios se guardan en Configuracion con clave 'anuncios'.
    Formato JSON: [{"texto": "...", "link": "...", "link_texto": "...", "activo": true}, ...]
    """
    anuncios_activos = []
    
    try:
        anuncios_json = Configuracion.get_valor('anuncios', '[]')
        anuncios = json.loads(anuncios_json)
        # Filtrar solo los activos
        anuncios_activos = [a for a in anuncios if a.get('activo', True)]
    except (json.JSONDecodeError, Exception):
        pass
    
    return {
        'anuncios_activos': anuncios_activos
    }
