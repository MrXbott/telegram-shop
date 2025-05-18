from flask import current_app, render_template, send_from_directory

from . import routes_bp

@routes_bp.route('/media/<path:filename>')
def media_files(filename):
    MEDIA_FOLDER_PATH = current_app.config.get('MEDIA_FOLDER_PATH')
    return send_from_directory(MEDIA_FOLDER_PATH, filename)

@routes_bp.route('/')
def admin_main():
    return render_template('admin_main.html')

