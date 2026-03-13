# generators/model_generator.py
# Genera classi Model C# da schema Access

from jinja2 import Environment, FileSystemLoader
from utils.naming import table_name_to_class, column_name_to_property, safe_property_name
from extractors.type_mapper import is_string_type
import os


def get_jinja_env(templates_dir):
    """Crea l'ambiente Jinja2 con i template dalla directory specificata."""
    return Environment(
        loader=FileSystemLoader(templates_dir),
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )


def build_model_context(table_info, namespace):
    """
    Costruisce il contesto Jinja2 per il template Model.cs.j2.
    
    Args:
        table_info: Dizionario con info tabella (name, columns, primary_keys, foreign_keys)
        namespace: Namespace del progetto
    
    Returns:
        Dizionario con il contesto per il template
    """
    class_name = table_name_to_class(table_info['name'])
    properties = []

    for col in table_info['columns']:
        prop_name = safe_property_name(col['name'])
        csharp_type = col['csharp_type']
        is_pk = col['is_primary_key']
        is_auto = col['is_auto_increment']
        original_name = col['name']
        max_length = col.get('max_length')
        nullable = col.get('nullable', True)

        annotations = []
        if is_pk:
            annotations.append('[Key]')
        if is_auto:
            annotations.append('[DatabaseGenerated(DatabaseGeneratedOption.Identity)]')
        if not nullable and not is_pk:
            annotations.append('[Required]')
        if is_string_type(csharp_type) and max_length and max_length > 0 and max_length < 32767:
            annotations.append(f'[StringLength({max_length})]')
        # Aggiunge [Column] solo se il nome originale differisce dal nome della proprietà
        if original_name != prop_name:
            escaped = original_name.replace('"', '\\"')
            annotations.append(f'[Column("{escaped}")]')

        properties.append({
            'name': prop_name,
            'original_name': original_name,
            'type': csharp_type,
            'annotations': annotations,
            'is_pk': is_pk,
            'is_auto': is_auto,
            'nullable': nullable,
        })

    # Proprietà di navigazione per le FK
    navigation_properties = []
    for fk in table_info.get('foreign_keys', []):
        ref_class = table_name_to_class(fk['pk_table'])
        fk_prop = safe_property_name(fk['fk_column'])
        navigation_properties.append({
            'type': ref_class,
            'name': ref_class,
            'fk_property': fk_prop,
        })

    return {
        'namespace': namespace,
        'class_name': class_name,
        'table_name': table_info['name'],
        'properties': properties,
        'navigation_properties': navigation_properties,
    }


def generate_model(table_info, namespace, templates_dir):
    """
    Genera il codice C# per la classe Model.
    
    Returns:
        Stringa con il codice C#
    """
    env = get_jinja_env(templates_dir)
    template = env.get_template('Model.cs.j2')
    context = build_model_context(table_info, namespace)
    return template.render(**context)
