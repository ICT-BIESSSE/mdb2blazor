# generators/page_generator.py
# Genera pagine Razor CRUD per ogni tabella

from jinja2 import Environment, FileSystemLoader
from utils.naming import table_name_to_class, table_name_to_variable, safe_property_name
from extractors.type_mapper import get_input_component, is_bool_type, is_date_type, is_numeric_type


def get_jinja_env(templates_dir):
    return Environment(
        loader=FileSystemLoader(templates_dir),
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )


def build_page_context(table_info, namespace):
    """Costruisce il contesto per i template delle pagine Razor."""
    class_name = table_name_to_class(table_info['name'])
    var_name = table_name_to_variable(table_info['name'])

    # Trova la PK
    pk_column = None
    for col in table_info['columns']:
        if col['is_primary_key']:
            pk_column = col
            break
    if pk_column is None and table_info['columns']:
        pk_column = table_info['columns'][0]

    pk_type = pk_column['csharp_type'].rstrip('?') if pk_column else 'int'
    pk_prop = safe_property_name(pk_column['name']) if pk_column else 'Id'

    # Costruisci info colonne per i form
    form_fields = []
    display_fields = []

    for col in table_info['columns']:
        prop_name = safe_property_name(col['name'])
        csharp_type = col['csharp_type']
        input_component = get_input_component(csharp_type)
        
        field_info = {
            'prop_name': prop_name,
            'label': col['name'],
            'type': csharp_type,
            'input_component': input_component,
            'is_pk': col['is_primary_key'],
            'is_auto': col['is_auto_increment'],
            'nullable': col.get('nullable', True),
            'is_bool': is_bool_type(csharp_type),
            'is_date': is_date_type(csharp_type),
            'is_numeric': is_numeric_type(csharp_type),
        }

        display_fields.append(field_info)

        # Nei form escludiamo le colonne auto-increment
        if not col['is_auto_increment']:
            form_fields.append(field_info)

    return {
        'namespace': namespace,
        'class_name': class_name,
        'var_name': var_name,
        'table_name': table_info['name'],
        'pk_type': pk_type,
        'pk_prop': pk_prop,
        'display_fields': display_fields,
        'form_fields': form_fields,
    }


def generate_list_page(table_info, namespace, templates_dir):
    env = get_jinja_env(templates_dir)
    template = env.get_template('List.razor.j2')
    context = build_page_context(table_info, namespace)
    return template.render(**context)


def generate_create_page(table_info, namespace, templates_dir):
    env = get_jinja_env(templates_dir)
    template = env.get_template('Create.razor.j2')
    context = build_page_context(table_info, namespace)
    return template.render(**context)


def generate_edit_page(table_info, namespace, templates_dir):
    env = get_jinja_env(templates_dir)
    template = env.get_template('Edit.razor.j2')
    context = build_page_context(table_info, namespace)
    return template.render(**context)


def generate_delete_page(table_info, namespace, templates_dir):
    env = get_jinja_env(templates_dir)
    template = env.get_template('Delete.razor.j2')
    context = build_page_context(table_info, namespace)
    return template.render(**context)
