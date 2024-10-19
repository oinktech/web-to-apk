import os
import zipfile
import subprocess
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_files():
    app_name = request.form.get('appName')
    app_version = request.form.get('appVersion')
    app_icon = request.files.get('appIcon')
    web_files = request.files.get('webFiles')

    # Validate input
    if not app_name or not app_version or not app_icon or not web_files:
        return jsonify({"error": "All fields are required."}), 400

    # Save files
    icon_path = os.path.join(UPLOAD_FOLDER, secure_filename(app_icon.filename))
    app_icon.save(icon_path)

    web_files_path = os.path.join(UPLOAD_FOLDER, secure_filename(web_files.filename))
    web_files.save(web_files_path)

    # Unzip web files
    web_files_folder = os.path.join(UPLOAD_FOLDER, 'web_files')
    os.makedirs(web_files_folder, exist_ok=True)
    with zipfile.ZipFile(web_files_path, 'r') as zip_ref:
        zip_ref.extractall(web_files_folder)

    # Generate build_apk.sh script
    apk_script_path = os.path.join(UPLOAD_FOLDER, 'build_apk.sh')
    with open(apk_script_path, 'w') as f:
        f.write(f'''#!/bin/bash
APP_NAME="{app_name}"
APP_VERSION="{app_version}"
ICON_PATH="{icon_path}"
WEB_FILES_PATH="{web_files_folder}"
OUTPUT_APK="{UPLOAD_FOLDER}/{app_name}.apk"

# Use Cordova to generate APK
cordova create "$APP_NAME" com.example."$APP_NAME" "$APP_NAME"
cd "$APP_NAME"

# Replace icon and web content
cp "$ICON_PATH" ./res/icon.png
cp -r "$WEB_FILES_PATH"/* ./www/

# Configure APK info
cordova platform add android
cordova build android --release

# Move the generated APK to the target path
cp ./platforms/android/app/build/outputs/apk/release/app-release.apk "$OUTPUT_APK"
''')

    # Grant execution permission
    os.chmod(apk_script_path, 0o755)

    # Run the APK build script
    result = subprocess.run([apk_script_path], capture_output=True, text=True)

    if result.returncode == 0:
        return send_file(f"{UPLOAD_FOLDER}/{app_name}.apk", as_attachment=True)
    else:
        return jsonify({"error": f"APK build failed: {result.stderr}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
