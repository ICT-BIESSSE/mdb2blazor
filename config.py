# config.py
# Configurazione globale per mdb2blazor

import os

# Percorso Python 32-bit (Windows)
PYTHON32_PATH = r"C:\Python32\python.exe"

# Percorso predefinito del file .mdb
DEFAULT_MDB_PATH = r"C:\py\GEST_ODBC.mdb"

# Cartella output predefinita
DEFAULT_OUTPUT_DIR = r"C:\py\BlazorOutput"

# Namespace predefinito per il progetto generato
DEFAULT_NAMESPACE = "BlazorApp"

# Versione target .NET
DOTNET_TARGET = "net10.0"

# Versione EntityFrameworkCore
EF_VERSION = "10.0.0"

# Encoding per i file .cs generati (UTF-8 con BOM)
CS_ENCODING = "utf-8-sig"

# Encoding per i file non-.cs generati (UTF-8 senza BOM)
DEFAULT_ENCODING = "utf-8"

# Stringa di connessione ODBC Access
ODBC_DRIVER = "Microsoft Access Driver (*.mdb)"

# Template directory (relativa alla root del progetto)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
