# mdb2blazor

Strumento Python 32-bit per convertire database Microsoft Access 97 (.mdb) in progetti Blazor Server C# .NET 10 completi, con pagine CRUD per ogni tabella.

## Descrizione

**mdb2blazor** legge lo schema di un database Access tramite ODBC e genera automaticamente:
- Classi **Model** C# con Data Annotations (Key, Required, StringLength, Column)
- **AppDbContext** EF Core con tutti i DbSet
- **Servizi** con interfacce (GetAllAsync, GetByIdAsync, CreateAsync, UpdateAsync, DeleteAsync)
- **Pagine Razor** CRUD (List, Create, Edit, Delete) per ogni tabella
- **Program.cs** con configurazione DI e middleware
- **appsettings.json** con connection string
- **Layout** e **NavMenu** con link a tutte le tabelle

## Prerequisiti

| Componente | Versione | Note |
|---|---|---|
| Python **32-bit** | 3.x | Installato in `C:\Python32\python.exe` |
| Microsoft Access Database Engine | 32-bit | Driver ODBC: `Microsoft Access Driver (*.mdb)` |
| .NET SDK | 10.0 | Per compilare il progetto generato |
| Sistema Operativo | Windows | Richiesto per il driver ODBC Access |

## Installazione

1. **Clona il repository:**
   ```bat
   cd C:\py
   git clone https://github.com/ICT-BIESSSE/mdb2blazor.git
   cd mdb2blazor
   ```

2. **Installa le dipendenze Python (32-bit):**
   ```bat
   install.bat
   ```
   Oppure manualmente:
   ```bat
   C:\Python32\python.exe -m pip install -r requirements.txt
   ```

## Utilizzo

```bat
run.bat --mdb "C:\percorso\database.mdb" --output "C:\output" --namespace "NomeProgetto"
```

### Parametri

| Parametro | Obbligatorio | Descrizione |
|---|---|---|
| `--mdb` | ✅ | Percorso al file `.mdb` da convertire |
| `--output` | ✅ | Cartella dove verrà creato il progetto |
| `--namespace` | ❌ | Namespace C# del progetto (default: `BlazorApp`) |
| `--seed` | ❌ | Estrae dati di esempio per il seeding |

### Esempio completo

```bat
run.bat --mdb "C:\py\GEST_ODBC.mdb" --output "C:\py\BlazorOutput" --namespace "GestApp"
```

Output atteso:
```
============================================================
  mdb2blazor - Generatore Blazor da Access .mdb
============================================================
  Database    : C:\py\GEST_ODBC.mdb
  Output      : C:\py\BlazorOutput
  Namespace   : GestApp
  Seeding     : No
============================================================

Estrazione schema dal database...
  Elaborazione tabella: Clienti
  Elaborazione tabella: Ordini
  ...

Trovate 5 tabelle:
  - Clienti (8 colonne, PK: ID)
  - Ordini (6 colonne, PK: IDOrdine)
  ...

Generazione progetto in: C:\py\BlazorOutput\GestApp

  Generazione file per: Clienti...
  Generazione file per: Ordini...
  ...
  Generazione AppDbContext...
  Generazione Program.cs...

Scrittura di 42 file su disco...

============================================================
  Generazione completata!
============================================================
  Tabelle processate : 5
  File generati      : 42
  Progetto in        : C:\py\BlazorOutput\GestApp
```

## Struttura del progetto generato

```
output/{NomeProgetto}/
├── {NomeProgetto}.csproj        # Progetto .NET 10 con pacchetti NuGet
├── Program.cs                   # Configurazione DI e middleware
├── appsettings.json             # Connection string verso .mdb
├── appsettings.Development.json
├── _Imports.razor               # Import globali Razor
├── Models/
│   └── {Tabella}.cs             # Una classe Model per ogni tabella
├── Data/
│   ├── AppDbContext.cs          # DbContext EF Core
│   └── Services/
│       ├── I{Tabella}Service.cs # Interfaccia servizio
│       └── {Tabella}Service.cs  # Implementazione servizio
├── Pages/
│   ├── _Host.cshtml
│   ├── Error.razor
│   └── {Tabella}/
│       ├── List.razor           # Elenco record con pulsanti Edit/Delete
│       ├── Create.razor         # Form creazione nuovo record
│       ├── Edit.razor           # Form modifica record esistente
│       └── Delete.razor         # Conferma eliminazione
├── Shared/
│   ├── MainLayout.razor         # Layout principale
│   ├── MainLayout.razor.css
│   └── NavMenu.razor            # Menu con link a tutte le tabelle
└── wwwroot/
    └── css/
        └── app.css
```

## Compilazione del progetto generato

```bat
cd "C:\py\BlazorOutput\GestApp"
dotnet restore
dotnet build
dotnet run
```

Poi apri il browser su `https://localhost:5001`.

## Mappatura tipi Access → C#

| Tipo Access | Codice ODBC | Tipo C# |
|---|---|---|
| TEXT / VARCHAR | 12 | `string` |
| MEMO / LONGCHAR | -1 | `string` |
| BYTE | -6 | `byte` |
| SHORT / INTEGER | 5 | `short` |
| LONG / COUNTER | 4 | `int` |
| SINGLE | 7 | `float` |
| DOUBLE | 8 | `double` |
| CURRENCY | 2 | `decimal` |
| YESNO / BIT | -7 | `bool` |
| DATETIME | 93 | `DateTime` |
| GUID | -11 | `Guid` |
| BINARY / LONGBINARY | -2, -3, -4 | `byte[]` |
| COUNTER (AutoNumber) | 4 | `int` + `[Key]` + `[DatabaseGenerated]` |

I tipi nullable (colonne che ammettono NULL) ottengono il suffisso `?` (es. `int?`, `DateTime?`).

## Struttura del progetto Python

```
mdb2blazor/
├── main.py                    # Entry point: parsing args, orchestrazione
├── config.py                  # Configurazione (percorsi, encoding, ecc.)
├── requirements.txt           # pyodbc>=4.0.39, Jinja2>=3.1.2
├── install.bat                # Installa dipendenze con Python 32-bit
├── run.bat                    # Lancia main.py con Python 32-bit
├── extractors/
│   ├── schema_extractor.py    # Connessione ODBC, estrazione tabelle/colonne/PK/FK
│   ├── data_extractor.py      # Estrazione dati per seeding (opzionale)
│   └── type_mapper.py         # Mappatura tipi ODBC → C#
├── generators/
│   ├── model_generator.py     # Genera classi Model C#
│   ├── dbcontext_generator.py # Genera AppDbContext EF Core
│   ├── service_generator.py   # Genera Service + IService
│   ├── page_generator.py      # Genera pagine Razor CRUD
│   ├── program_generator.py   # Genera Program.cs, appsettings.json, .csproj
│   └── project_generator.py   # Genera file condivisi (Layout, NavMenu, CSS)
├── templates/                 # Template Jinja2
│   ├── Model.cs.j2
│   ├── DbContext.cs.j2
│   ├── Service.cs.j2
│   ├── IService.cs.j2
│   ├── List.razor.j2
│   ├── Create.razor.j2
│   ├── Edit.razor.j2
│   ├── Delete.razor.j2
│   ├── Program.cs.j2
│   ├── appsettings.json.j2
│   ├── Project.csproj.j2
│   ├── MainLayout.razor.j2
│   ├── NavMenu.razor.j2
│   └── _Imports.razor.j2
└── utils/
    ├── naming.py              # PascalCase, pluralizzazione, sanitizzazione
    └── file_writer.py         # Scrittura file UTF-8 / UTF-8 con BOM
```

## Troubleshooting

### Errore: "Data source name not found"
**Causa:** Il driver ODBC 32-bit non è installato o Python non è 32-bit.

**Soluzione:**
1. Verifica di usare `C:\Python32\python.exe` (32-bit)
2. Scarica e installa **Microsoft Access Database Engine 2010 Redistributable (32-bit)**:
   - URL: https://www.microsoft.com/en-us/download/details.aspx?id=13255
3. Verifica che il driver sia disponibile:
   ```bat
   C:\Python32\python.exe -c "import pyodbc; print([d for d in pyodbc.drivers() if 'Access' in d])"
   ```
   Dovrebbe mostrare: `['Microsoft Access Driver (*.mdb)']`

### Errore: "File not found" per il .mdb
**Causa:** Percorso non corretto o file non accessibile.

**Soluzione:**
- Verifica il percorso esatto: `dir "C:\percorso\file.mdb"`
- Usa virgolette per i percorsi con spazi: `--mdb "C:\My Folder\database.mdb"`

### Errore di compilazione .NET: "EntityFrameworkCore.Jet not found"
**Causa:** Pacchetti NuGet non ancora disponibili per .NET 10.

**Soluzione:**
Modifica `{NomeProgetto}.csproj` per usare la versione compatibile disponibile e adatta `Program.cs` di conseguenza.

### Tabelle con nomi speciali (spazi, caratteri non ASCII)
I nomi vengono automaticamente convertiti in PascalCase valido per C#. Il nome originale della tabella viene preservato nell'attributo `[Table("nome_originale")]` del Model.

### Encoding file .cs
I file `.cs` e `.razor` vengono scritti in **UTF-8 con BOM** (`utf-8-sig`) per compatibilità con Visual Studio. Gli altri file (`.json`, `.csproj`, ecc.) vengono scritti in UTF-8 senza BOM.

## Licenza

MIT License - Vedi file LICENSE per i dettagli.
