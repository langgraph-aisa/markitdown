import os
from flask import Flask, request, jsonify, render_template_string
from markitdown import MarkItDown

app = Flask(__name__)
md = MarkItDown()

# Interfaz HTML con Drag and Drop - Personalizada para AISA
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AISA - Conversor a Markdown</title>
    <style>
        /* --- ESTILOS CORPORATIVOS AISA (azul y naranja) --- */
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            background: #f0f2f5; 
            margin: 0; 
            padding: 20px; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
        }
        .container { 
            background: white; 
            padding: 35px; 
            border-radius: 20px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.08); 
            max-width: 750px; 
            width: 100%; 
            transition: all 0.2s;
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 4px solid #003366; 
            padding-bottom: 20px; 
        }
        .header h1 { 
            color: #003366; 
            margin: 0; 
            font-size: 28px; 
            letter-spacing: -0.5px;
        }
        .header h1 span { color: #ff6600; }
        .header p { 
            color: #555; 
            margin: 8px 0 0; 
            font-size: 16px; 
        }
        #drop-zone { 
            border: 2px dashed #003366; 
            border-radius: 16px; 
            padding: 50px 20px; 
            background: #f8fbff; 
            text-align: center; 
            cursor: pointer; 
            transition: all 0.3s ease; 
        }
        #drop-zone.dragover { 
            background: #e6eefa; 
            border-color: #ff6600; 
            transform: scale(1.01);
        }
        #drop-zone p { 
            margin: 0; 
            font-size: 18px; 
            color: #003366; 
            font-weight: 500;
        }
        #drop-zone .icon { 
            font-size: 52px; 
            display: block; 
            margin-bottom: 12px; 
        }
        #drop-zone .sub { 
            font-size: 14px; 
            color: #888; 
            font-weight: normal; 
            margin-top: 8px; 
        }
        #file-input { display: none; }

        #loading { 
            display: none; 
            text-align: center; 
            margin-top: 25px; 
        }
        .spinner { 
            border: 5px solid #f3f3f3; 
            border-radius: 50%; 
            border-top: 5px solid #003366; 
            width: 40px; 
            height: 40px; 
            animation: spin 1s linear infinite; 
            margin: 0 auto 10px; 
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #loading p { color: #003366; font-weight: 600; }

        #result-container { 
            margin-top: 30px; 
            display: none; 
        }
        #result-container h3 { 
            color: #003366; 
            margin-bottom: 10px; 
            font-size: 18px; 
            display: flex; 
            align-items: center; 
            gap: 8px; 
        }
        textarea { 
            width: 100%; 
            height: 280px; 
            padding: 14px; 
            border: 1px solid #d0d7de; 
            border-radius: 12px; 
            font-family: 'Courier New', monospace; 
            font-size: 14px; 
            resize: vertical; 
            background: #fafbfc; 
            line-height: 1.6;
        }
        .btn-group { 
            display: flex; 
            gap: 12px; 
            margin-top: 12px; 
            flex-wrap: wrap; 
        }
        .btn { 
            background: #003366; 
            color: white; 
            border: none; 
            padding: 10px 24px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: 600; 
            font-size: 14px; 
            transition: all 0.2s; 
            display: inline-flex; 
            align-items: center; 
            gap: 6px; 
        }
        .btn:hover { background: #ff6600; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(255,102,0,0.3); }
        .btn-outline { 
            background: transparent; 
            color: #003366; 
            border: 2px solid #003366; 
        }
        .btn-outline:hover { background: #003366; color: white; box-shadow: none; }

        .footer { 
            text-align: center; 
            margin-top: 30px; 
            font-size: 13px; 
            color: #888; 
            border-top: 1px solid #e9ecf0; 
            padding-top: 20px; 
        }
        .footer a { color: #003366; text-decoration: none; font-weight: 500; }
        .footer a:hover { color: #ff6600; }
        .alert { 
            padding: 12px 18px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            display: none; 
        }
        .alert-error { background: #fee; color: #b00; border: 1px solid #fcc; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <!-- Logo o nombre de AISA -->
            <h1>🔄 <span>AISA</span> · Markdown Converter</h1>
            <p>Convierte tus manuales técnicos a Markdown con un solo arrastre</p>
        </div>

        <div id="alert-box" class="alert alert-error"></div>

        <div id="drop-zone">
            <span class="icon">📂</span>
            <p>Arrastra tu archivo aquí o haz clic para seleccionarlo</p>
            <span class="sub">PDF, Word, Excel, PowerPoint, Imágenes y más</span>
            <input type="file" id="file-input">
        </div>

        <div id="loading">
            <div class="spinner"></div>
            <p>Procesando archivo... esto puede tomar unos segundos</p>
        </div>

        <div id="result-container">
            <h3>📝 Resultado en Markdown</h3>
            <textarea id="output-result" readonly></textarea>
            <div class="btn-group">
                <button class="btn" onclick="copyToClipboard()">📋 Copiar</button>
                <button class="btn btn-outline" onclick="downloadMarkdown()">⬇️ Descargar .md</button>
                <button class="btn btn-outline" onclick="resetApp()">🔄 Nuevo archivo</button>
            </div>
        </div>

        <div class="footer">
            Desarrollado para <a href="https://www.aisa.com.gt/" target="_blank">AISA Guatemala</a> · 
            Tecnología <a href="https://github.com/microsoft/markitdown" target="_blank">MarkItDown</a> · 
            Desplegado en Google Cloud Run
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const loading = document.getElementById('loading');
        const resultContainer = document.getElementById('result-container');
        const outputResult = document.getElementById('output-result');
        const alertBox = document.getElementById('alert-box');

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                handleFile(fileInput.files[0]);
            }
        });

        function handleFile(file) {
            // Validar tamaño (máximo 10 MB)
            if (file.size > 10 * 1024 * 1024) {
                showAlert('El archivo es demasiado grande. Máximo 10 MB.', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            loading.style.display = 'block';
            resultContainer.style.display = 'none';
            hideAlert();

            fetch('/convert', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loading.style.display = 'none';
                if (data.error) {
                    showAlert('Error: ' + data.error, 'error');
                } else {
                    outputResult.value = data.markdown;
                    resultContainer.style.display = 'block';
                }
            })
            .catch(error => {
                loading.style.display = 'none';
                showAlert('Error de red: ' + error.message, 'error');
            });
        }

        function copyToClipboard() {
            outputResult.select();
            document.execCommand('copy');
            showAlert('✅ Texto copiado al portapapeles', 'success');
            setTimeout(hideAlert, 3000);
        }

        function downloadMarkdown() {
            const content = outputResult.value;
            if (!content) return;
            const blob = new Blob([content], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'converted.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        function resetApp() {
            resultContainer.style.display = 'none';
            outputResult.value = '';
            fileInput.value = '';
            hideAlert();
        }

        function showAlert(msg, type) {
            alertBox.textContent = msg;
            alertBox.style.display = 'block';
            alertBox.className = 'alert alert-' + type;
        }

        function hideAlert() {
            alertBox.style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/convert", methods=["POST"])
def convert_file():
    if "file" not in request.files:
        return jsonify({"error": "No se encontró ningún archivo"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    # Guardar temporalmente
    temp_path = os.path.join("/tmp", file.filename)
    file.save(temp_path)

    try:
        result = md.convert(temp_path)
        return jsonify({
            "filename": file.filename,
            "markdown": result.text_content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
