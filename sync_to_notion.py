import os
import glob
from notion_client import Client

NOTION_SECRET = os.environ.get('NOTION_SECRET')
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

if not NOTION_SECRET or not DATABASE_ID:
    print("❌ Error: Faltan variables de entorno")
    exit(1)

print(f"🔑 Secreto: {NOTION_SECRET[:10]}...")
print(f"📚 Base de datos ID: {DATABASE_ID}")

# Forzar versión de API que soporta markdown
notion = Client(auth=NOTION_SECRET, notion_version="2025-05-13")
print("✅ Cliente inicializado")

archivos_md = glob.glob('**/*.md', recursive=True)
print(f"📁 Archivos .md encontrados: {len(archivos_md)}")

for filepath in archivos_md:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        print(f"📝 Procesando: {filename}")

        # Crear nueva página en la base de datos
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": filename}}]}
            },
            markdown=content
        )
        print(f"✅ Creado: {filename}")
        
    except Exception as e:
        print(f"❌ Error con {filename}: {e}")
        # Intentar imprimir más detalles si la excepción tiene respuesta
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"   Detalles: {e.response.text}")

print("🎉 Proceso completado")
