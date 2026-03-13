# utils/file_writer.py
# Scrive file su disco con encoding appropriato

import os
import sys


def write_file(path, content, encoding='utf-8'):
    """Scrive un file su disco con l'encoding specificato."""
    # Crea le directory intermedie se non esistono
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(path, 'w', encoding=encoding) as f:
        f.write(content)


def write_cs_file(path, content):
    """Scrive un file .cs con UTF-8 con BOM (richiesto per compatibilità MSVS)."""
    write_file(path, content, encoding='utf-8-sig')


def write_razor_file(path, content):
    """Scrive un file .razor con UTF-8 con BOM."""
    write_file(path, content, encoding='utf-8-sig')


def write_text_file(path, content):
    """Scrive un file di testo generico con UTF-8 senza BOM."""
    write_file(path, content, encoding='utf-8')


def write_files(file_map, base_dir=''):
    """
    Scrive più file dato un dizionario {percorso_relativo: contenuto}.
    Se base_dir è specificato, i percorsi sono relativi a quella directory.
    """
    written = []
    for rel_path, content in file_map.items():
        if base_dir:
            full_path = os.path.join(base_dir, rel_path)
        else:
            full_path = rel_path

        # Scegli l'encoding in base all'estensione
        ext = os.path.splitext(full_path)[1].lower()
        if ext in ('.cs', '.razor', '.csproj'):
            write_cs_file(full_path, content)
        else:
            write_text_file(full_path, content)

        written.append(full_path)

    return written
