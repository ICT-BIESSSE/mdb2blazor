# extractors/data_extractor.py
# Estrae dati dalle tabelle (opzionale, per seeding)

import pyodbc
from .schema_extractor import connect


def extract_table_data(mdb_path, table_name, max_rows=100):
    """
    Estrae i dati da una tabella Access.
    
    Args:
        mdb_path: Percorso del file .mdb
        table_name: Nome della tabella
        max_rows: Numero massimo di righe da estrarre (default: 100)
    
    Returns:
        Tupla (colonne, righe) dove:
        - colonne: lista di nomi di colonna
        - righe: lista di tuple con i valori
    """
    conn = connect(mdb_path)
    cursor = conn.cursor()

    try:
        # Escapa il nome della tabella con [] per gestire spazi e caratteri speciali
        query = f"SELECT TOP {max_rows} * FROM [{table_name}]"
        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        return columns, [tuple(row) for row in rows]

    except pyodbc.Error as e:
        print(f"  Attenzione: impossibile estrarre dati da '{table_name}': {e}")
        return [], []

    finally:
        cursor.close()
        conn.close()


def extract_all_data(mdb_path, table_names, max_rows=100):
    """
    Estrae i dati da tutte le tabelle specificate.
    
    Args:
        mdb_path: Percorso del file .mdb
        table_names: Lista di nomi di tabelle
        max_rows: Numero massimo di righe per tabella
    
    Returns:
        Dizionario {nome_tabella: {'columns': [...], 'rows': [...]}}
    """
    result = {}

    for table_name in table_names:
        print(f"  Estrazione dati tabella: {table_name}")
        columns, rows = extract_table_data(mdb_path, table_name, max_rows)
        result[table_name] = {
            'columns': columns,
            'rows': rows,
        }

    return result


def generate_seed_sql(table_name, columns, rows, class_name):
    """
    Genera codice C# per il seeding dei dati (metodo HasData di EF Core).
    
    Returns:
        Stringa con il codice C# per il seeding
    """
    if not rows:
        return ''

    lines = []
    lines.append(f'            modelBuilder.Entity<{class_name}>().HasData(')

    for i, row in enumerate(rows):
        values = []
        for col, val in zip(columns, row):
            if val is None:
                values.append(f'                {col} = null')
            elif isinstance(val, str):
                escaped = val.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                values.append(f'                {col} = "{escaped}"')
            elif isinstance(val, bool):
                values.append(f'                {col} = {"true" if val else "false"}')
            elif isinstance(val, (int, float)):
                values.append(f'                {col} = {val}')
            else:
                values.append(f'                {col} = "{val}"')

        comma = ',' if i < len(rows) - 1 else ''
        lines.append(f'            new {class_name}')
        lines.append('            {')
        lines.append(',\n'.join(values))
        lines.append('            }' + comma)

    lines.append('            );')

    return '\n'.join(lines)
