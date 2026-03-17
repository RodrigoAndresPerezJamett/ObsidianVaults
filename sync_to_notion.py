import os
import glob
from notion_client import Client

NOTION_SECRET = os.environ.get('NOTION_SECRET')
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')  # Cambiamos a DATABASE_ID

if not NOTION_SECRET or not DATABASE_ID:
    print("❌ Error: Faltan variables de entorno")
    exit(1)

print(f"🔑 Secreto: {NOTION_SECRET[:10]}...")
print(f"📚 Base de datos ID: {DATABASE_ID}")

notion = Client(auth=NOTION_SECRET, notion_version="2025-05-13")  # Versión que soporta markdown

# Obtener todas las páginas existentes en la base de datos (para evitar duplicados)
existing_pages = {}
try:
    results = notion.databases.query(database_id=DATABASE_ID).get("results", [])
    for page in results:
        title_prop = page["properties"].get("Name", {}).get("title", [])
        if title_prop:
            title = title_prop[0]["text"]["content"]
            existing_pages[title] = page["id"]
    print(f"📄 Páginas existentes: {len(existing_pages)}")
except Exception as e:
    print(f"⚠️ No se pudo obtener la lista existente: {e}")

# Procesar archivos .md
archivos_md = glob.glob('**/*.md', recursive=True)
print(f"📁 Archivos .md encontrados: {len(archivos_md)}")

for filepath in archivos_md:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        print(f"📝 Procesando: {filename}")

        # Propiedades comunes
        properties = {
            "Name": {"title": [{"text": {"content": filename}}]}
        }

        if filename in existing_pages:
            # Actualizar página existente
            page_id = existing_pages[filename]
            notion.pages.update(
                page_id=page_id,
                properties=properties,
                markdown=content
            )
            print(f"🔄 Actualizado: {filename}")
        else:
            # Crear nueva página en la base de datos
            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties=properties,
                markdown=content
            )
            print(f"✅ Creado: {filename}")
        
    except Exception as e:
        print(f"❌ Error con {filepath}: {str(e)}")

print("🎉 Proceso completado")
