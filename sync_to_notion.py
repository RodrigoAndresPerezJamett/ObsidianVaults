import os
import glob
from notion_client import Client

# Configuración desde variables de entorno
NOTION_TOKEN = os.environ['NOTION_TOKEN']
PAGE_ID = os.environ['NOTION_PAGE_ID']

notion = Client(auth=NOTION_TOKEN)

# Leer todos los archivos .md en el repositorio (incluyendo subcarpetas)
for filepath in glob.glob('**/*.md', recursive=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    print(f"Procesando: {filename}")
    
    # Crear subpágina en Notion
    notion.pages.create(
        parent={"page_id": PAGE_ID},
        properties={
            "title": {"title": [{"text": {"content": filename}}]}
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                }
            }
        ]
    )
    print(f"✅ Subido: {filename}")
