# generators/dbcontext_generator.py
# Genera DbContext EF Core

from jinja2 import Environment, FileSystemLoader
from utils.naming import table_name_to_class, pluralize


def get_jinja_env(templates_dir):
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )
    return env


def generate_dbcontext(tables_info, namespace, templates_dir):
    """
    Genera il codice C# per AppDbContext.
    
    Args:
        tables_info: Lista di dizionari con info tabelle
        namespace: Namespace del progetto
        templates_dir: Directory dei template Jinja2
    
    Returns:
        Stringa con il codice C#
    """
    env = get_jinja_env(templates_dir)
    template = env.get_template('DbContext.cs.j2')

    db_sets = []
    for table in tables_info:
        class_name = table_name_to_class(table['name'])
        db_set_name = pluralize(class_name)
        db_sets.append({
            'class_name': class_name,
            'db_set_name': db_set_name,
            'table_name': table['name'],
        })

    context = {
        'namespace': namespace,
        'db_sets': db_sets,
    }

    return template.render(**context)
