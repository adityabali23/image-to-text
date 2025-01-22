from flask import Flask, request, render_template
import lalala  # Import your model file
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error_text="No file uploaded.")

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error_text="No selected file.")

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the uploaded image
        try:
            details = lalala.process_image(file_path)
            return render_template('index.html', details=details, image_path=file_path)
        except Exception as e:
            return render_template('index.html', error_text=f"Error: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
