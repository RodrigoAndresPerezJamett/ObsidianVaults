import os
import glob
from notion_client import Client

# Obtener variables de entorno (ahora usa NOTION_SECRET)
NOTION_SECRET = os.environ.get('NOTION_SECRET')
PAGE_ID = os.environ.get('NOTION_PAGE_ID')

if not NOTION_SECRET:
    print("❌ Error: La variable NOTION_SECRET no está definida")
    exit(1)

if not PAGE_ID:
    print("❌ Error: La variable NOTION_PAGE_ID no está definida")
    exit(1)

print(f"🔑 Secreto comienza con: {NOTION_SECRET[:10]}...")
print(f"📄 ID de página: {PAGE_ID}")

# Inicializar cliente de Notion
notion = Client(auth=NOTION_SECRET)

# Buscar todos los archivos .md
archivos_md = glob.glob('**/*.md', recursive=True)
print(f"📁 Archivos .md encontrados: {len(archivos_md)}")

if not archivos_md:
    print("⚠️ No se encontraron archivos .md en el repositorio")
    exit(0)

for filepath in archivos_md:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        print(f"📝 Procesando: {filename}")
        
        # Crear página en Notion
        response = notion.pages.create(
            parent={"page_id": PAGE_ID},
            properties={
                "title": {
                    "title": [{"text": {"content": filename}}]
                }
            },
            markdown=content
        )
        
        print(f"✅ Subido: {filename} (ID: {response['id']})")
        
    except Exception as e:
        print(f"❌ Error con {filepath}: {str(e)}")

print("🎉 Proceso completado")
