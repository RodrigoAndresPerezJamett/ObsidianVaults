import os
import glob
import requests
import json

NOTION_SECRET = os.environ.get('NOTION_SECRET')
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

if not NOTION_SECRET or not DATABASE_ID:
    print("❌ Error: Faltan variables de entorno")
    exit(1)

print(f"🔑 Secreto: {NOTION_SECRET[:10]}...")
print(f"📚 Base de datos ID: {DATABASE_ID}")

headers = {
    "Authorization": f"Bearer {NOTION_SECRET}",
    "Content-Type": "application/json",
    "Notion-Version": "2025-05-13"  # Versión que soporta markdown
}

# Obtener páginas existentes para evitar duplicados
existing_pages = {}
try:
    query_payload = {
        "filter": {
            "property": "Name",
            "title": {
                "is_not_empty": True
            }
        }
    }
    response = requests.post(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        headers=headers,
        json=query_payload
    )
    if response.status_code == 200:
        data = response.json()
        for page in data.get("results", []):
            title_prop = page["properties"].get("Name", {}).get("title", [])
            if title_prop:
                title = title_prop[0]["text"]["content"]
                existing_pages[title] = page["id"]
        print(f"📄 Páginas existentes: {len(existing_pages)}")
    else:
        print(f"⚠️ No se pudo consultar la base de datos: {response.status_code} - {response.text}")
except Exception as e:
    print(f"⚠️ Error al consultar: {e}")

# Procesar archivos .md
archivos_md = glob.glob('**/*.md', recursive=True)
print(f"📁 Archivos .md encontrados: {len(archivos_md)}")

for filepath in archivos_md:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        filename = os.path.basename(filepath)
        print(f"📝 Procesando: {filename}")

        # Preparar payload
        payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": filename}}]
                }
            },
            "markdown": content
        }

        if filename in existing_pages:
            # Actualizar página existente (PATCH)
            page_id = existing_pages[filename]
            url = f"https://api.notion.com/v1/pages/{page_id}"
            response = requests.patch(url, headers=headers, json=payload)
            if response.status_code == 200:
                print(f"🔄 Actualizado: {filename}")
            else:
                print(f"❌ Error actualizando {filename}: {response.status_code} - {response.text}")
        else:
            # Crear nueva página (POST)
            url = "https://api.notion.com/v1/pages"
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                print(f"✅ Creado: {filename}")
                # Agregar al diccionario para futuras actualizaciones en la misma ejecución
                data = response.json()
                existing_pages[filename] = data["id"]
            else:
                print(f"❌ Error creando {filename}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error con {filepath}: {str(e)}")

print("🎉 Proceso completado")
