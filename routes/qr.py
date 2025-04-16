from flask import Blueprint, request, jsonify, current_app, send_file, render_template
from flask_login import login_required, current_user
from models import QRCode
from extensions import db
import qrcode
from datetime import datetime
import uuid
import os

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/dashboard')
@login_required
def dashboard():
    qr_codes = QRCode.query.filter_by(user_id=current_user.id).order_by(QRCode.generated_at.desc()).all()
    return render_template('dashboard.html', qr_codes=qr_codes)

@qr_bp.route('/generate_qr', methods=['POST'])
@login_required
def generate_qr():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400

    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    filename = f"qr_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
    file_path = os.path.join(current_app.static_folder, 'qr_codes', filename)

    try:
        qr_image.save(file_path)
    except Exception:
        return jsonify({'error': 'Failed to save QR code image'}), 500

    qr_code = QRCode(user_id=current_user.id, input_url=url, qr_filename=filename)
    db.session.add(qr_code)
    db.session.commit()

    return jsonify({
        'message': 'QR code generated successfully',
        'qr_code': {
            'id': qr_code.id,
            'url': url,
            'filename': filename,
            'generated_at': qr_code.generated_at.isoformat()
        }
    }), 201

@qr_bp.route('/download/<int:qr_id>')
@login_required
def download_qr(qr_id):
    qr_code = QRCode.query.get_or_404(qr_id)
    if qr_code.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    file_path = os.path.join(current_app.static_folder, 'qr_codes', qr_code.qr_filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True)

@qr_bp.route('/qr_history')
@login_required
def qr_history():
    qr_codes = QRCode.query.filter_by(user_id=current_user.id).order_by(QRCode.generated_at.desc()).all()
    history = [{
        'id': qr.id,
        'url': qr.input_url,
        'filename': qr.qr_filename,
        'generated_at': qr.generated_at.isoformat()
    } for qr in qr_codes]
    return jsonify({'qr_codes': history})
