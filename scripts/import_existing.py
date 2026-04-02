#!/usr/bin/env python3
"""
Narratium — Importar novela existente
Importa una biblia narrativa, archivo de continuidad, y/o capítulos ya escritos.
El script prepara los datos para que el LLM los analice y pueble la DB.

FLUJO:
1. Este script lee los archivos y los prepara
2. Claude Code analiza el contenido con el LLM
3. Claude Code usa los otros scripts para poblar la DB

Este script NO puebla la DB directamente — genera un JSON de importación
que Claude Code debe revisar con el autor antes de aplicar.
"""

import argparse
import json
import os
import sys
import glob
import re


def read_file(path: str) -> str:
    """Lee un archivo de texto."""
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"No se pudo leer {path} con ninguna codificación conocida")


def extract_docx_text(path: str) -> str:
    """Extrae texto de un .docx usando pandoc si está disponible, o zipfile."""
    # Intentar con pandoc primero
    import subprocess
    try:
        result = subprocess.run(['pandoc', path, '-t', 'markdown', '--wrap=none'],
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Fallback: extraer texto básico del XML
    import zipfile
    with zipfile.ZipFile(path, 'r') as z:
        with z.open('word/document.xml') as f:
            content = f.read().decode('utf-8')
            # Extraer texto entre tags <w:t>
            texts = re.findall(r'<w:t[^>]*>(.*?)</w:t>', content)
            return '\n'.join(texts)


def prepare_import(bible_path: str = None, continuity_path: str = None,
                   chapters_dir: str = None) -> dict:
    """Prepara los datos de importación."""
    
    import_data = {
        "status": "ready_for_analysis",
        "bible": None,
        "continuity": None,
        "chapters": [],
        "instructions": []
    }
    
    # Biblia narrativa
    if bible_path and os.path.exists(bible_path):
        ext = os.path.splitext(bible_path)[1].lower()
        if ext == '.docx':
            content = extract_docx_text(bible_path)
        elif ext in ('.md', '.txt'):
            content = read_file(bible_path)
        else:
            content = read_file(bible_path)
        
        import_data["bible"] = {
            "path": bible_path,
            "content_length": len(content),
            "content_preview": content[:2000] + "..." if len(content) > 2000 else content,
            "full_content": content
        }
        import_data["instructions"].append(
            "BIBLIA CARGADA. Claude Code debe analizar la biblia para extraer: "
            "personajes (con fichas completas), localizaciones, hechos narrativos, "
            "hilos principales, relaciones entre personajes, y reglas de estilo específicas. "
            "Mostrar al autor para confirmación antes de insertar en la DB."
        )
    
    # Archivo de continuidad
    if continuity_path and os.path.exists(continuity_path):
        content = read_file(continuity_path)
        import_data["continuity"] = {
            "path": continuity_path,
            "content_length": len(content),
            "content_preview": content[:2000] + "..." if len(content) > 2000 else content,
            "full_content": content
        }
        import_data["instructions"].append(
            "CONTINUIDAD CARGADA. Claude Code debe analizar para extraer: "
            "estado epistémico de cada personaje, pistas plantadas con su estado, "
            "beats de hilos por capítulo, y eventos del mundo. "
            "Cruzar con la biblia para consistencia."
        )
    
    # Capítulos existentes
    if chapters_dir and os.path.isdir(chapters_dir):
        patterns = ['*.md', '*.txt', '*.docx']
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(chapters_dir, pattern)))
        
        files.sort()
        
        for filepath in files:
            filename = os.path.basename(filepath)
            # Intentar extraer número de capítulo del nombre
            match = re.search(r'(\d+)', filename)
            chapter_num = int(match.group(1)) if match else None
            
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.docx':
                content = extract_docx_text(filepath)
            else:
                content = read_file(filepath)
            
            import_data["chapters"].append({
                "path": filepath,
                "filename": filename,
                "chapter_number": chapter_num,
                "word_count": len(content.split()),
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "full_content": content
            })
        
        if import_data["chapters"]:
            import_data["instructions"].append(
                f"{len(import_data['chapters'])} CAPÍTULOS ENCONTRADOS. "
                "Claude Code debe analizar cada capítulo para extraer eventos, "
                "cambios epistémicos, beats de hilos, y pistas. "
                "Procesar en orden cronológico."
            )
    
    return import_data


def main():
    parser = argparse.ArgumentParser(description="Importar novela existente a Narratium")
    parser.add_argument("--bible", default=None, help="Ruta a la biblia narrativa (.docx, .md, .txt)")
    parser.add_argument("--continuity", default=None, help="Ruta al archivo de continuidad (.md, .txt)")
    parser.add_argument("--chapters-dir", default=None, help="Directorio con capítulos (.md, .txt, .docx)")
    parser.add_argument("--db", required=True, help="Ruta a la base de datos SQLite")
    
    args = parser.parse_args()
    
    if not any([args.bible, args.continuity, args.chapters_dir]):
        print(json.dumps({"status": "error", "message": "Especifica al menos --bible, --continuity, o --chapters-dir"}))
        sys.exit(1)
    
    result = prepare_import(args.bible, args.continuity, args.chapters_dir)
    
    # Para el output, no incluir full_content (demasiado largo)
    output = json.loads(json.dumps(result, ensure_ascii=False))
    if output.get("bible"):
        output["bible"].pop("full_content", None)
    if output.get("continuity"):
        output["continuity"].pop("full_content", None)
    for ch in output.get("chapters", []):
        ch.pop("full_content", None)
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
