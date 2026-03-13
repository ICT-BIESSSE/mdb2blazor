# generators/service_generator.py
# Genera servizi C# e interfacce per ogni tabella

from jinja2 import Environment, FileSystemLoader
from utils.naming import table_name_to_class, pluralize


def get_jinja_env(templates_dir):
    return Environment(
        loader=FileSystemLoader(templates_dir),
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )


def build_service_context(table_info, namespace):
    """Costruisce il contesto per i template Service e IService."""
    class_name = table_name_to_class(table_info['name'])
    
    # Trova la colonna PK
    pk_column = None
    for col in table_info['columns']:
        if col['is_primary_key']:
            pk_column = col
            break
    
    # Se non c'è PK definita, usa la prima colonna
    if pk_column is None and table_info['columns']:
        pk_column = table_info['columns'][0]

    pk_type = pk_column['csharp_type'].rstrip('?') if pk_column else 'int'
    pk_name = table_name_to_class(pk_column['name']) if pk_column else 'Id'

    return {
        'namespace': namespace,
        'class_name': class_name,
        'pk_type': pk_type,
        'pk_name': pk_name,
    }


def generate_service(table_info, namespace, templates_dir):
    """Genera il codice C# per il servizio."""
    env = get_jinja_env(templates_dir)
    template = env.get_template('Service.cs.j2')
    context = build_service_context(table_info, namespace)
    return template.render(**context)


def generate_iservice(table_info, namespace, templates_dir):
    """Genera il codice C# per l'interfaccia del servizio."""
    env = get_jinja_env(templates_dir)
    template = env.get_template('IService.cs.j2')
    context = build_service_context(table_info, namespace)
    return template.render(**context)
