from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import subprocess
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    app_name = request.form['app_name']
    icon_file = request.files['icon']
    web_files = request.files.getlist('web_files')

    if not app_name or not icon_file or not web_files:
        return jsonify({'error': 'Please provide app name, icon, and web files.'}), 400

    icon_path = os.path.join(app.config['UPLOAD_FOLDER'], icon_file.filename)
    icon_file.save(icon_path)

    web_file_paths = []
    for web_file in web_files:
        web_file_path = os.path.join(app.config['UPLOAD_FOLDER'], web_file.filename)
        web_file.save(web_file_path)
        web_file_paths.append(web_file_path)

    build_script = f"""#!/bin/bash
    cd {UPLOAD_FOLDER}
    cordova create {app_name}
    cd {app_name}
    cordova platform add android
    mkdir -p www
    cp -r ../* www/
    cordova build android --release
    """
    
    with open('build_apk.sh', 'w') as f:
        f.write(build_script)

    subprocess.run(['bash', 'build_apk.sh'], check=True)

    apk_filename = f"{app_name}/platforms/android/app/build/outputs/apk/release/app-release-unsigned.apk"
    
    if os.path.exists(apk_filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], apk_filename, as_attachment=True)
    else:
        return jsonify({'error': 'Failed to build APK. Please check the logs.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000,debug=True)
