# utils/naming.py
# Utility per la gestione dei nomi: PascalCase, pluralizzazione, sanitizzazione

import re


def to_pascal_case(name):
    """Converte un nome in PascalCase, rimuovendo caratteri non validi."""
    # Sostituisce caratteri non alfanumerici con spazi
    name = re.sub(r'[^a-zA-Z0-9\s_]', ' ', name)
    # Divide per spazi, underscore
    parts = re.split(r'[\s_]+', name)
    # Capitalizza ogni parte
    result = ''.join(part.capitalize() for part in parts if part)
    # Se inizia con un numero, aggiunge prefisso
    if result and result[0].isdigit():
        result = 'T' + result
    return result or 'Unknown'


def to_camel_case(name):
    """Converte un nome in camelCase."""
    pascal = to_pascal_case(name)
    if pascal:
        return pascal[0].lower() + pascal[1:]
    return pascal


def sanitize_identifier(name):
    """Rimuove caratteri non validi per un identificatore C#."""
    # Sostituisce caratteri non alfanumerici/underscore con underscore
    result = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Rimuove underscore multipli
    result = re.sub(r'_+', '_', result)
    # Rimuove underscore iniziale/finale
    result = result.strip('_')
    # Se inizia con un numero, aggiunge prefisso
    if result and result[0].isdigit():
        result = 'F' + result
    return result or 'Unknown'


def pluralize(name):
    """Pluralizzazione semplice in inglese per nomi di tabelle (case-insensitive)."""
    if not name:
        return name
    lower = name.lower()
    # Regole di pluralizzazione basilari
    if lower.endswith('y') and len(name) > 1 and lower[-2] not in 'aeiou':
        return name[:-1] + 'ies'
    elif lower.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return name + 'es'
    else:
        return name + 's'


def table_name_to_class(table_name):
    """Converte il nome di una tabella Access in un nome di classe C# valido."""
    return to_pascal_case(table_name)


def table_name_to_variable(table_name):
    """Converte il nome di una tabella in un nome di variabile camelCase."""
    return to_camel_case(table_name)


def column_name_to_property(column_name):
    """Converte il nome di una colonna Access in un nome di proprietà C# valido."""
    return to_pascal_case(column_name)


def is_csharp_keyword(name):
    """Controlla se il nome è una parola chiave C#."""
    keywords = {
        'abstract', 'as', 'base', 'bool', 'break', 'byte', 'case', 'catch',
        'char', 'checked', 'class', 'const', 'continue', 'decimal', 'default',
        'delegate', 'do', 'double', 'else', 'enum', 'event', 'explicit',
        'extern', 'false', 'finally', 'fixed', 'float', 'for', 'foreach',
        'goto', 'if', 'implicit', 'in', 'int', 'interface', 'internal', 'is',
        'lock', 'long', 'namespace', 'new', 'null', 'object', 'operator', 'out',
        'override', 'params', 'private', 'protected', 'public', 'readonly',
        'ref', 'return', 'sbyte', 'sealed', 'short', 'sizeof', 'stackalloc',
        'static', 'string', 'struct', 'switch', 'this', 'throw', 'true', 'try',
        'typeof', 'uint', 'ulong', 'unchecked', 'unsafe', 'ushort', 'using',
        'virtual', 'void', 'volatile', 'while'
    }
    return name.lower() in keywords


def safe_property_name(name):
    """Restituisce un nome di proprietà sicuro per C# (evita parole chiave)."""
    prop = column_name_to_property(name)
    if is_csharp_keyword(prop.lower()):
        prop = prop + 'Value'
    return prop
