from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import io
import subprocess
import tempfile
import shutil

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_pdf_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PDF_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert-image', methods=['POST', 'OPTIONS'])
def convert_image():
    if request.method == 'OPTIONS':
        return '', 200
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    target_format = request.form.get('format')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not allowed_image_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 415

    try:
        # Open source image
        image = Image.open(file)

        # Normalize target format name for Pillow
        fmt_map = {
            'jpg': 'JPEG',
            'jpeg': 'JPEG',
            'png': 'PNG',
            'webp': 'WEBP'
        }

        target = target_format.lower()
        if target not in fmt_map:
            return 'Unsupported target format', 400

        pil_format = fmt_map[target]

        # Handle transparency when converting to JPEG (no alpha channel)
        if pil_format == 'JPEG':
            # If the image has an alpha channel, composite it over white background
            if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                alpha = image.convert('RGBA').split()[-1]
                bg = Image.new('RGB', image.size, (255, 255, 255))
                bg.paste(image.convert('RGBA'), mask=alpha)
                image_out = bg
            else:
                image_out = image.convert('RGB')
        else:
            # For PNG/WebP keep mode where possible
            if image.mode == 'P':
                image_out = image.convert('RGBA') if 'transparency' in image.info else image.convert('RGB')
            else:
                image_out = image

        # Save to bytes buffer with sensible quality settings
        output = io.BytesIO()
        save_kwargs = {}
        if pil_format == 'JPEG':
            save_kwargs.update({'format': 'JPEG', 'quality': 85, 'optimize': True})
        elif pil_format == 'WEBP':
            save_kwargs.update({'format': 'WEBP', 'quality': 85})
        else:
            save_kwargs.update({'format': pil_format, 'optimize': True})

        # Pillow accepts format as separate arg or in kwargs; use save with kwargs
        image_out.save(output, **save_kwargs)
        output.seek(0)

        # Generate output filename using original base name when possible
        original_name = getattr(file, 'filename', None) or 'converted'
        base = os.path.splitext(original_name)[0]
        output_filename = f"{base}.{target}"

        # Set mimetype for response
        mimetype_map = {'jpeg': 'image/jpeg', 'jpg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}

        return send_file(
            output,
            as_attachment=True,
            download_name=output_filename,
            mimetype=mimetype_map.get(target, f'image/{target}')
        )

    except Exception as e:
        return str(e), 500

@app.route('/compress-pdf', methods=['POST', 'OPTIONS'])
def compress_pdf():
    if request.method == 'OPTIONS':
        return '', 200

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not allowed_pdf_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 415

    # compression level from form: screen, ebook, printer, prepress
    level = request.form.get('level', 'ebook')

    try:
        # Attempt Ghostscript compression if available for better results
        gs_exec = shutil.which('gswin64c') or shutil.which('gs') or shutil.which('gswin32c')
        if gs_exec:
            # Write uploaded PDF to a temp file
            with tempfile.TemporaryDirectory() as td:
                in_path = os.path.join(td, 'in.pdf')
                out_path = os.path.join(td, 'out.pdf')
                # Ensure file stream is at beginning
                file.stream.seek(0)
                with open(in_path, 'wb') as f:
                    f.write(file.read())

                # Map level to Ghostscript PDFSETTINGS
                settings_map = {
                    'screen': '/screen',   # lowest quality, smallest size
                    'ebook': '/ebook',     # medium quality
                    'printer': '/printer', # high quality
                    'prepress': '/prepress' # highest quality, least compression
                }
                pdf_setting = settings_map.get(level, '/ebook')

                # Build Ghostscript command. For more aggressive compression, add explicit
                # downsampling flags for raster images depending on selected level.
                gs_cmd = [
                    gs_exec,
                    '-sDEVICE=pdfwrite',
                    '-dCompatibilityLevel=1.4',
                    f'-dPDFSETTINGS={pdf_setting}',
                    '-dNOPAUSE', '-dBATCH'
                ]

                # Add explicit downsampling parameters for non-prepress settings
                if level in ('screen', 'ebook', 'printer'):
                    # target DPI per level
                    dpi_map = {'screen': 72, 'ebook': 100, 'printer': 150}
                    dpi = dpi_map.get(level, 100)
                    gs_cmd += [
                        '-dDownsampleColorImages=true',
                        '-dDownsampleGrayImages=true',
                        '-dDownsampleMonoImages=true',
                        f'-dColorImageResolution={dpi}',
                        f'-dGrayImageResolution={dpi}',
                        f'-dMonoImageResolution={dpi}',
                        '-dColorImageDownsampleType=/Average',
                        '-dGrayImageDownsampleType=/Average'
                    ]

                gs_cmd += [f'-sOutputFile={out_path}', in_path]

                # Run Ghostscript and capture output for debugging
                try:
                    subprocess.run(gs_cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError as gs_err:
                    # include stderr for diagnosis
                    stderr = gs_err.stderr.decode('utf-8', errors='ignore') if gs_err.stderr else ''
                    raise RuntimeError(f'Ghostscript failed (rc={gs_err.returncode}): {stderr}') from gs_err

                # Read compressed output
                with open(out_path, 'rb') as outf:
                    data = outf.read()
                output = io.BytesIO(data)
                output.seek(0)

                return send_file(
                    output,
                    as_attachment=True,
                    download_name='compressed.pdf',
                    mimetype='application/pdf'
                )

        # Fallback: attempt PyPDF2 streaming compression (limited)
        file.stream.seek(0)
        pdf_reader = PdfReader(file)
        pdf_writer = PdfWriter()
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        output = io.BytesIO()
        try:
            pdf_writer.write(output, compress_streams=True)
        except TypeError:
            pdf_writer.write(output)
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name='compressed.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        # If Ghostscript subprocess failed, include hint
        msg = str(e)
        if isinstance(e, subprocess.CalledProcessError):
            msg = f'Ghostscript failed: return code {e.returncode}. Check that gs is installed and accessible.'
        return msg, 500

@app.route('/merge-pdf', methods=['POST', 'OPTIONS'])
def merge_pdf():
    if request.method == 'OPTIONS':
        return '', 200

    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    try:
        merger = PdfMerger()
        
        for file in files:
            if not allowed_pdf_file(file.filename):
                return f'Invalid file type: {file.filename}', 400
            merger.append(file)
        
        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        merger.close()
        
        return send_file(
            output,
            as_attachment=True,
            download_name='merged.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)