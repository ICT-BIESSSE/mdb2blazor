# extractors/schema_extractor.py
# Estrae schema tabelle da un database Access via ODBC

import pyodbc
from .type_mapper import map_type


def get_connection_string(mdb_path):
    """Costruisce la stringa di connessione ODBC per un file .mdb."""
    return (
        r"DRIVER={Microsoft Access Driver (*.mdb)};"
        f"DBQ={mdb_path};"
        "PWD=;"
    )


def connect(mdb_path):
    """Apre una connessione ODBC al file .mdb specificato."""
    conn_str = get_connection_string(mdb_path)
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        return conn
    except pyodbc.Error as e:
        raise ConnectionError(
            f"Impossibile connettersi al database '{mdb_path}'.\n"
            f"Errore ODBC: {e}\n\n"
            "Verifica che:\n"
            "  1. Il file .mdb esiste ed è accessibile\n"
            "  2. Il driver 'Microsoft Access Driver (*.mdb)' 32-bit è installato\n"
            "  3. Stai usando Python 32-bit (C:\\Python32\\python.exe)\n"
        )


def get_tables(cursor):
    """Restituisce la lista delle tabelle utente (esclude tabelle di sistema)."""
    tables = []
    for row in cursor.tables():
        if row.table_type == 'TABLE':
            tables.append(row.table_name)
    return tables


def get_columns(cursor, table_name):
    """
    Restituisce le colonne di una tabella con tutte le informazioni necessarie.
    
    Returns:
        Lista di dizionari con:
        - name: nome colonna originale
        - type_code: codice tipo ODBC
        - type_name: nome tipo ODBC
        - nullable: bool
        - max_length: lunghezza massima (per stringhe)
        - is_primary_key: bool
        - is_auto_increment: bool
    """
    columns = []
    for col in cursor.columns(table=table_name):
        column = {
            'name': col.column_name,
            'type_code': col.data_type,
            'type_name': col.type_name if hasattr(col, 'type_name') else '',
            'nullable': col.nullable == 1,
            'max_length': col.column_size if col.column_size else None,
            'is_primary_key': False,
            'is_auto_increment': False,
            'ordinal': col.ordinal_position,
        }
        # Rileva AutoNumber (COUNTER)
        type_name = str(column['type_name']).upper()
        if 'COUNTER' in type_name or 'AUTOINCREMENT' in type_name:
            column['is_auto_increment'] = True

        columns.append(column)

    # Ordina per posizione ordinale
    columns.sort(key=lambda c: c.get('ordinal', 0))
    return columns


def get_primary_keys(cursor, table_name):
    """Restituisce il set dei nomi delle colonne che fanno parte della PK."""
    pk_columns = set()
    try:
        for stat in cursor.statistics(table=table_name):
            # INDEX_NAME contiene 'PrimaryKey' per le PK in Access
            index_name = stat.index_name if stat.index_name else ''
            if index_name.upper() == 'PRIMARYKEY' or 'PRIMARY' in index_name.upper():
                if stat.column_name:
                    pk_columns.add(stat.column_name)
    except Exception:
        pass

    # Fallback: usa primaryKeys se disponibile
    if not pk_columns:
        try:
            for pk in cursor.primaryKeys(table=table_name):
                if pk.column_name:
                    pk_columns.add(pk.column_name)
        except Exception:
            pass

    return pk_columns


def get_foreign_keys(cursor, table_name):
    """
    Restituisce le foreign key della tabella.
    
    Returns:
        Lista di dizionari con:
        - fk_column: colonna FK nella tabella corrente
        - pk_table: tabella referenziata
        - pk_column: colonna PK nella tabella referenziata
    """
    foreign_keys = []
    try:
        for fk in cursor.foreignKeys(table=table_name):
            foreign_keys.append({
                'fk_column': fk.fkcolumn_name,
                'pk_table': fk.pktable_name,
                'pk_column': fk.pkcolumn_name,
            })
    except Exception:
        pass
    return foreign_keys


def extract_schema(mdb_path):
    """
    Estrae lo schema completo del database .mdb.
    
    Returns:
        Lista di dizionari, uno per ogni tabella:
        {
            'name': nome tabella,
            'columns': lista colonne (vedi get_columns),
            'primary_keys': set nomi colonne PK,
            'foreign_keys': lista FK (vedi get_foreign_keys),
        }
    """
    conn = connect(mdb_path)
    cursor = conn.cursor()

    tables_info = []
    table_names = get_tables(cursor)

    for table_name in table_names:
        print(f"  Elaborazione tabella: {table_name}")

        columns = get_columns(cursor, table_name)
        pk_set = get_primary_keys(cursor, table_name)
        foreign_keys = get_foreign_keys(cursor, table_name)

        # Aggiorna le colonne con informazioni PK
        for col in columns:
            if col['name'] in pk_set:
                col['is_primary_key'] = True

        # Se non troviamo la PK tramite statistics/primaryKeys,
        # proviamo a rilevare colonne AutoNumber come PK implicita
        has_pk = any(c['is_primary_key'] for c in columns)
        if not has_pk:
            for col in columns:
                if col['is_auto_increment']:
                    col['is_primary_key'] = True
                    break

        # Mappa i tipi C# per ogni colonna
        for col in columns:
            col['csharp_type'] = map_type(
                col['type_code'],
                nullable=col['nullable'] and not col['is_primary_key'],
                is_counter=col['is_auto_increment']
            )

        tables_info.append({
            'name': table_name,
            'columns': columns,
            'primary_keys': pk_set,
            'foreign_keys': foreign_keys,
        })

    cursor.close()
    conn.close()

    return tables_info
