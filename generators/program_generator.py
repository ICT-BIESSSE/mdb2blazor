# generators/program_generator.py
# Genera Program.cs con DI e configurazione Blazor Server

from jinja2 import Environment, FileSystemLoader
from utils.naming import table_name_to_class


def get_jinja_env(templates_dir):
    return Environment(
        loader=FileSystemLoader(templates_dir),
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )


def generate_program(tables_info, namespace, templates_dir):
    """
    Genera Program.cs per il progetto Blazor Server.
    
    Args:
        tables_info: Lista di dizionari con info tabelle
        namespace: Namespace del progetto
        templates_dir: Directory dei template Jinja2
    
    Returns:
        Stringa con il codice C#
    """
    env = get_jinja_env(templates_dir)
    template = env.get_template('Program.cs.j2')

    services = []
    for table in tables_info:
        class_name = table_name_to_class(table['name'])
        services.append(class_name)

    context = {
        'namespace': namespace,
        'services': services,
    }

    return template.render(**context)


def generate_appsettings(mdb_path, namespace, templates_dir):
    """Genera appsettings.json con la connection string."""
    env = get_jinja_env(templates_dir)
    template = env.get_template('appsettings.json.j2')

    # Escape per JSON: backslash -> \\
    mdb_path_json = mdb_path.replace('\\', '\\\\')

    context = {
        'namespace': namespace,
        'mdb_path': mdb_path_json,
    }

    return template.render(**context)


def generate_csproj(namespace, templates_dir):
    """Genera il file .csproj per il progetto Blazor Server .NET 10."""
    env = get_jinja_env(templates_dir)
    template = env.get_template('Project.csproj.j2')

    context = {
        'namespace': namespace,
    }

    return template.render(**context)
