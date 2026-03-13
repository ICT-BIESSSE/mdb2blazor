# extractors/type_mapper.py
# Mappa tipi ODBC/Access -> C#

# Mappatura codici tipo ODBC -> tipo C#
ODBC_TYPE_MAP = {
    12: 'string',      # TEXT/VARCHAR
    -1: 'string',      # MEMO/LONGCHAR
    -6: 'byte',        # BYTE
    5:  'short',       # SHORT/INTEGER
    4:  'int',         # LONG/COUNTER
    7:  'float',       # SINGLE
    8:  'double',      # DOUBLE
    2:  'decimal',     # CURRENCY/NUMERIC
    -7: 'bool',        # YESNO/BIT
    93: 'DateTime',    # DATETIME/TIMESTAMP
    -11: 'Guid',       # GUID/UNIQUEIDENTIFIER
    -2: 'byte[]',      # BINARY
    -3: 'byte[]',      # VARBINARY
    -4: 'byte[]',      # LONGBINARY/IMAGE
    1:  'string',      # CHAR
    6:  'float',       # FLOAT
    3:  'decimal',     # DECIMAL
    9:  'DateTime',    # DATE
    10: 'TimeSpan',    # TIME
    91: 'DateTime',    # DATE (SQL)
    92: 'TimeSpan',    # TIME (SQL)
    -9: 'string',      # NVARCHAR
    -8: 'string',      # NCHAR
    -10: 'string',     # NTEXT
    16: 'bool',        # BIT (alternativo)
}

# Tipi che non supportano nullable con ? (value types che comunque hanno senso nullable)
VALUE_TYPES = {'byte', 'short', 'int', 'long', 'float', 'double', 'decimal', 'bool', 'DateTime', 'TimeSpan', 'Guid'}

# Tipi reference (già nullable senza ?)
REFERENCE_TYPES = {'string', 'byte[]'}


def map_type(odbc_type_code, nullable=True, is_counter=False):
    """
    Mappa un codice tipo ODBC nel corrispondente tipo C#.
    
    Args:
        odbc_type_code: Codice numerico del tipo ODBC
        nullable: Se True, aggiunge ? ai value types nullable
        is_counter: Se True, forza il tipo a int (AutoNumber)
    
    Returns:
        Stringa con il tipo C# corrispondente
    """
    if is_counter:
        return 'int'

    csharp_type = ODBC_TYPE_MAP.get(odbc_type_code, 'string')

    # Per i value types, aggiungi ? se nullable
    if nullable and csharp_type in VALUE_TYPES:
        return csharp_type + '?'

    return csharp_type


def get_input_component(csharp_type):
    """
    Restituisce il componente Blazor InputBase appropriato per il tipo C#.
    
    Args:
        csharp_type: Tipo C# (eventualmente con ?)
    
    Returns:
        Nome del componente Blazor (es. InputText, InputNumber, ecc.)
    """
    # Rimuove il ? nullable
    base_type = csharp_type.rstrip('?')

    component_map = {
        'string': 'InputText',
        'int': 'InputNumber',
        'short': 'InputNumber',
        'long': 'InputNumber',
        'byte': 'InputNumber',
        'float': 'InputNumber',
        'double': 'InputNumber',
        'decimal': 'InputNumber',
        'bool': 'InputCheckbox',
        'DateTime': 'InputDate',
        'DateOnly': 'InputDate',
        'TimeSpan': 'InputText',
        'Guid': 'InputText',
        'byte[]': 'InputText',
    }

    return component_map.get(base_type, 'InputText')


def is_numeric_type(csharp_type):
    """Controlla se il tipo C# è numerico."""
    base_type = csharp_type.rstrip('?')
    return base_type in {'int', 'short', 'long', 'byte', 'float', 'double', 'decimal'}


def is_string_type(csharp_type):
    """Controlla se il tipo C# è stringa."""
    return csharp_type.rstrip('?') == 'string'


def is_bool_type(csharp_type):
    """Controlla se il tipo C# è booleano."""
    return csharp_type.rstrip('?') == 'bool'


def is_date_type(csharp_type):
    """Controlla se il tipo C# è una data/ora."""
    return csharp_type.rstrip('?') in {'DateTime', 'DateOnly', 'TimeSpan'}


def get_default_value(csharp_type):
    """Restituisce il valore di default per il tipo C#."""
    base_type = csharp_type.rstrip('?')
    nullable = csharp_type.endswith('?')

    if nullable:
        return 'null'

    defaults = {
        'string': '""',
        'int': '0',
        'short': '0',
        'long': '0',
        'byte': '0',
        'float': '0f',
        'double': '0.0',
        'decimal': '0m',
        'bool': 'false',
        'DateTime': 'DateTime.MinValue',
        'TimeSpan': 'TimeSpan.Zero',
        'Guid': 'Guid.Empty',
        'byte[]': 'Array.Empty<byte>()',
    }

    return defaults.get(base_type, 'default')
