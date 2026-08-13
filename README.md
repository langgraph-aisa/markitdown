# AISA MarkItDown Converter

Aplicación web especializada para convertir manuales técnicos a Markdown, con interfaz drag-and-drop, desplegada en Google Cloud Run.

## Características
- Conversión de múltiples formatos (PDF, Word, Excel, PowerPoint, imágenes, etc.)
- Interfaz drag-and-drop intuitiva
- Copiar y descargar resultado en Markdown
- Despliegue automático desde GitHub a Cloud Run
- Capa gratuita de Google Cloud (Always Free)

## Tecnologías
- Python + Flask
- Microsoft MarkItDown
- Google Cloud Run
- Docker

## Despliegue en Cloud Run
1. Sube este repositorio a GitHub.
2. Conecta tu repositorio en Google Cloud Run (selecciona "Desplegar desde repositorio").
3. Elige la región `us-central1` y permite invocaciones no autenticadas.
4. Haz clic en Crear. ¡Listo!

## Uso local
```bash
pip install -r requirements.txt
python app.py
