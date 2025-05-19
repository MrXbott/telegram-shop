from flask import current_app, render_template, send_from_directory
import logging

from . import routes_bp

logger = logging.getLogger(__name__)

@routes_bp.route('/media/<path:filename>')
def media_files(filename):
    MEDIA_FOLDER_PATH = current_app.config.get('MEDIA_FOLDER_PATH')
    logger.info(f'📦 Запрос медиа-файла: {filename}')
    return send_from_directory(MEDIA_FOLDER_PATH, filename)

@routes_bp.route('/')
def admin_main():
    logger.info('🛠 Отображение главной страницы админки')
    return render_template('admin_main.html')

