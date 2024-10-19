from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import subprocess

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

    # 创建应用名称的目录
    app_upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], app_name)
    if not os.path.exists(app_upload_folder):
        os.makedirs(app_upload_folder)

    icon_path = os.path.join(app_upload_folder, icon_file.filename)
    icon_file.save(icon_path)

    web_file_paths = []
    for web_file in web_files:
        web_file_path = os.path.join(app_upload_folder, web_file.filename)
        web_file.save(web_file_path)
        web_file_paths.append(web_file_path)

    # 生成 build_apk.sh 脚本
    build_script = f"""#!/bin/bash
    cd {app_upload_folder}
    cordova create {app_name}
    cd {app_name}
    cordova platform add android
    mkdir -p www
    cp -r ../* www/
    cp -r ../uploads/* www/uploads/  # 确保uploads目录不会被复制到自身
    cordova build android --release
    """

    with open(os.path.join(app_upload_folder, 'build_apk.sh'), 'w') as f:
        f.write(build_script)
    
    # 修改权限
    os.chmod(os.path.join(app_upload_folder, 'build_apk.sh'), 0o755)

    # 运行脚本
    try:
        subprocess.run(['bash', 'build_apk.sh'], check=True, cwd=app_upload_folder)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Build failed: {e}'})

    apk_filename = os.path.join(app_upload_folder, app_name, "platforms", "android", "app", "build", "outputs", "apk", "release", "app-release-unsigned.apk")
    
    if os.path.exists(apk_filename):
        return send_from_directory(app_upload_folder, apk_filename, as_attachment=True)
    else:
        return jsonify({'error': 'Failed to build APK. Please check the logs.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000,debug=True)
