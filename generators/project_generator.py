# generators/project_generator.py
# Genera la struttura del progetto Blazor Server .NET 10

import os
from jinja2 import Environment, FileSystemLoader
from utils.naming import table_name_to_class
from utils.file_writer import write_files


def get_jinja_env(templates_dir):
    return Environment(
        loader=FileSystemLoader(templates_dir),
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )


def generate_shared_files(namespace, templates_dir, tables_info):
    """
    Genera i file condivisi del progetto (Layout, NavMenu, _Imports, css).
    
    Returns:
        Dizionario {percorso_relativo: contenuto}
    """
    env = get_jinja_env(templates_dir)
    files = {}

    # Costruisce lista tabelle per il menu di navigazione
    table_classes = []
    for table in tables_info:
        class_name = table_name_to_class(table['name'])
        table_classes.append({
            'class_name': class_name,
            'table_name': table['name'],
        })

    nav_context = {
        'namespace': namespace,
        'tables': table_classes,
    }

    # MainLayout.razor
    main_layout_tpl = env.get_template('MainLayout.razor.j2')
    files['Shared/MainLayout.razor'] = main_layout_tpl.render(**nav_context)

    # MainLayout.razor.css (vuoto per ora)
    files['Shared/MainLayout.razor.css'] = ''

    # NavMenu.razor
    nav_tpl = env.get_template('NavMenu.razor.j2')
    files['Shared/NavMenu.razor'] = nav_tpl.render(**nav_context)

    # _Imports.razor
    imports_tpl = env.get_template('_Imports.razor.j2')
    files['_Imports.razor'] = imports_tpl.render(namespace=namespace)

    # wwwroot/css/app.css
    files['wwwroot/css/app.css'] = _get_app_css()

    return files


def _get_app_css():
    """Restituisce il CSS base per l'applicazione Blazor."""
    return """\
/* app.css - Stili base per l'applicazione Blazor */

html, body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

h1:focus {
    outline: none;
}

a, .btn-link {
    color: #0071c1;
}

.btn-primary {
    color: #fff;
    background-color: #1b6ec2;
    border-color: #1861ac;
}

.btn-sm {
    padding: 0.1rem 0.4rem;
    font-size: 0.75rem;
}

.content {
    padding-top: 1.1rem;
}

.valid.modified:not([type=checkbox]) {
    outline: 1px solid #26b050;
}

.invalid {
    outline: 1px solid red;
}

.validation-message {
    color: red;
}

#blazor-error-ui {
    background: lightyellow;
    bottom: 0;
    box-shadow: 0 -1px 2px rgba(0, 0, 0, 0.2);
    display: none;
    left: 0;
    padding: 0.6rem 1.25rem 0.7rem 1.25rem;
    position: fixed;
    width: 100%;
    z-index: 1000;
}

#blazor-error-ui .dismiss {
    cursor: pointer;
    position: absolute;
    right: 0.75rem;
    top: 0.5rem;
}

.table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
}

.table th, .table td {
    padding: 0.5rem;
    border: 1px solid #dee2e6;
}

.table th {
    background-color: #f8f9fa;
    font-weight: bold;
}

.table tr:hover {
    background-color: #f5f5f5;
}

.page-actions {
    margin-bottom: 1rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 500;
}

.form-control {
    display: block;
    width: 100%;
    padding: 0.375rem 0.75rem;
    font-size: 1rem;
    border: 1px solid #ced4da;
    border-radius: 0.25rem;
}
"""
