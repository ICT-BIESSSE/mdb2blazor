#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py - Entry point principale per mdb2blazor

Genera un progetto Blazor Server C# .NET 10 da un database Microsoft Access 97 (.mdb).

Utilizzo:
    C:/Python32/python.exe main.py --mdb <percorso.mdb> --output <cartella_output> --namespace <Namespace> [--seed]

Esempi:
    run.bat --mdb "C:/py/GEST_ODBC.mdb" --output "C:/py/BlazorOutput" --namespace "GestApp"
    run.bat --mdb "C:/dati/database.mdb" --output "C:/output" --namespace "MyBlazorApp" --seed
"""

import argparse
import os
import sys


def parse_args():
    """Analizza gli argomenti della riga di comando."""
    parser = argparse.ArgumentParser(
        description='Genera un progetto Blazor Server .NET 10 da un database Access .mdb',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--mdb',
        required=True,
        help='Percorso al file .mdb (es. C:\\py\\GEST_ODBC.mdb)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Cartella di output per il progetto Blazor generato'
    )
    parser.add_argument(
        '--namespace',
        default='BlazorApp',
        help='Namespace/nome del progetto C# (default: BlazorApp)'
    )
    parser.add_argument(
        '--seed',
        action='store_true',
        help='Estrae e include dati di esempio nel progetto (seeding)'
    )
    return parser.parse_args()


def check_mdb_file(mdb_path):
    """Verifica che il file .mdb esista e sia accessibile."""
    if not os.path.isfile(mdb_path):
        print(f"ERRORE: Il file '{mdb_path}' non esiste o non è accessibile.")
        print("Verifica il percorso e i permessi del file.")
        sys.exit(1)
    if not mdb_path.lower().endswith('.mdb'):
        print(f"ATTENZIONE: Il file '{mdb_path}' non ha estensione .mdb")


def create_output_dir(output_dir, namespace):
    """Crea la directory di output per il progetto."""
    project_dir = os.path.join(output_dir, namespace)
    try:
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
    except OSError as e:
        print(f"ERRORE: Impossibile creare la cartella di output '{project_dir}': {e}")
        sys.exit(1)


def main():
    """Funzione principale."""
    args = parse_args()

    mdb_path = os.path.abspath(args.mdb)
    output_dir = os.path.abspath(args.output)
    namespace = args.namespace
    seed = args.seed

    print("=" * 60)
    print("  mdb2blazor - Generatore Blazor da Access .mdb")
    print("=" * 60)
    print(f"  Database    : {mdb_path}")
    print(f"  Output      : {output_dir}")
    print(f"  Namespace   : {namespace}")
    print(f"  Seeding     : {'Sì' if seed else 'No'}")
    print("=" * 60)
    print()

    # 1. Verifica file .mdb
    check_mdb_file(mdb_path)

    # 2. Importa e configura i moduli (import tardivo per evitare errori se pyodbc non installato)
    try:
        from extractors.schema_extractor import extract_schema
    except ImportError as e:
        print(f"ERRORE: Impossibile importare i moduli necessari: {e}")
        print("Esegui prima 'install.bat' per installare le dipendenze.")
        sys.exit(1)

    from generators.model_generator import generate_model
    from generators.dbcontext_generator import generate_dbcontext
    from generators.service_generator import generate_service, generate_iservice
    from generators.page_generator import (
        generate_list_page, generate_create_page,
        generate_edit_page, generate_delete_page
    )
    from generators.program_generator import generate_program, generate_appsettings, generate_csproj
    from generators.project_generator import generate_shared_files
    from utils.naming import table_name_to_class
    from utils.file_writer import write_files
    from config import TEMPLATES_DIR
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        keep_trailing_newline=True,
    )

    # 3. Estrazione schema
    print("Estrazione schema dal database...")
    try:
        tables_info = extract_schema(mdb_path)
    except ConnectionError as e:
        print(f"\nERRORE di connessione:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRORE durante l'estrazione dello schema: {e}")
        sys.exit(1)

    if not tables_info:
        print("ATTENZIONE: Nessuna tabella trovata nel database.")
        sys.exit(0)

    print(f"\nTrovate {len(tables_info)} tabelle:")
    for t in tables_info:
        pk_cols = [c['name'] for c in t['columns'] if c['is_primary_key']]
        print(f"  - {t['name']} ({len(t['columns'])} colonne, PK: {', '.join(pk_cols) or 'nessuna'})")

    # 4. Crea la directory di output
    project_dir = create_output_dir(output_dir, namespace)
    print(f"\nGenerazione progetto in: {project_dir}")
    print()

    # 5. Genera i file
    all_files = {}
    file_count = 0

    for table in tables_info:
        class_name = table_name_to_class(table['name'])
        print(f"  Generazione file per: {class_name}...")

        # Model
        model_code = generate_model(table, namespace, TEMPLATES_DIR)
        all_files[f"Models/{class_name}.cs"] = model_code

        # Service + Interface
        iservice_code = generate_iservice(table, namespace, TEMPLATES_DIR)
        service_code = generate_service(table, namespace, TEMPLATES_DIR)
        all_files[f"Data/Services/I{class_name}Service.cs"] = iservice_code
        all_files[f"Data/Services/{class_name}Service.cs"] = service_code

        # Pagine CRUD
        list_code = generate_list_page(table, namespace, TEMPLATES_DIR)
        create_code = generate_create_page(table, namespace, TEMPLATES_DIR)
        edit_code = generate_edit_page(table, namespace, TEMPLATES_DIR)
        delete_code = generate_delete_page(table, namespace, TEMPLATES_DIR)
        all_files[f"Pages/{class_name}/List.razor"] = list_code
        all_files[f"Pages/{class_name}/Create.razor"] = create_code
        all_files[f"Pages/{class_name}/Edit.razor"] = edit_code
        all_files[f"Pages/{class_name}/Delete.razor"] = delete_code

    # DbContext
    print("  Generazione AppDbContext...")
    dbcontext_code = generate_dbcontext(tables_info, namespace, TEMPLATES_DIR)
    all_files["Data/AppDbContext.cs"] = dbcontext_code

    # Program.cs
    print("  Generazione Program.cs...")
    program_code = generate_program(tables_info, namespace, TEMPLATES_DIR)
    all_files["Program.cs"] = program_code

    # appsettings.json
    appsettings_code = generate_appsettings(mdb_path, namespace, TEMPLATES_DIR)
    all_files["appsettings.json"] = appsettings_code

    # .csproj
    csproj_code = generate_csproj(namespace, TEMPLATES_DIR)
    all_files[f"{namespace}.csproj"] = csproj_code

    # File condivisi (Layout, NavMenu, ecc.)
    print("  Generazione file condivisi...")
    shared_files = generate_shared_files(namespace, TEMPLATES_DIR, tables_info)
    all_files.update(shared_files)

    # Pages/_Host.cshtml (necessario per Blazor Server)
    host_template = env.get_template('_Host.cshtml.j2')
    all_files["Pages/_Host.cshtml"] = host_template.render(namespace=namespace)

    # Pages/Error.razor
    error_template = env.get_template('Error.razor.j2')
    all_files["Pages/Error.razor"] = error_template.render(namespace=namespace)

    # appsettings.Development.json
    all_files["appsettings.Development.json"] = '{\n  "Logging": {\n    "LogLevel": {\n      "Default": "Information",\n      "Microsoft.AspNetCore": "Warning"\n    }\n  }\n}\n'

    # 6. Scrivi i file su disco
    print(f"\nScrittura di {len(all_files)} file su disco...")
    written = write_files(all_files, base_dir=project_dir)
    file_count = len(written)

    # 7. Riepilogo finale
    print()
    print("=" * 60)
    print("  Generazione completata!")
    print("=" * 60)
    print(f"  Tabelle processate : {len(tables_info)}")
    print(f"  File generati      : {file_count}")
    print(f"  Progetto in        : {project_dir}")
    print()
    print("Per compilare ed eseguire il progetto:")
    print(f"  cd \"{project_dir}\"")
    print(f"  dotnet build")
    print(f"  dotnet run")
    print()
    print("NOTA: Prima di compilare, verifica la connessione al database")
    print("      in appsettings.json e installa i pacchetti NuGet:")
    print(f"  cd \"{project_dir}\"")
    print(f"  dotnet restore")
    print("=" * 60)


if __name__ == '__main__':
    main()
