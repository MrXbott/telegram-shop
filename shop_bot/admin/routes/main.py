from flask import current_app, render_template, request, redirect, url_for, send_from_directory
import logging

from . import routes_bp

logger = logging.getLogger(__name__)


@routes_bp.route('/media/<path:filename>')
def media_files(filename):
    MEDIA_FOLDER_PATH = current_app.config.get('MEDIA_FOLDER_PATH')
    return send_from_directory(MEDIA_FOLDER_PATH, filename)


@routes_bp.route('/')
def index():
    return render_template('index.html')

