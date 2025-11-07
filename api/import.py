# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Data import API"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.jwt import get_current_user_id
import pandas as pd
import io

from models import Host, db
from utils.decorators import validate_json

bp = Blueprint('import', __name__)


@bp.route('/csv/hosts', methods=['POST'])
@jwt_required()
def import_hosts_from_csv():
    """Import hosts from CSV file"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': 'No file selected'}), 400
    
    user_id = get_current_user_id()
    
    try:
        # Read CSV
        df = pd.read_csv(file, keep_default_na=False)
        
        # Validate required columns
        required_columns = ['ip']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            return jsonify({
                'code': 400,
                'message': f'Missing required columns: {", ".join(missing)}'
            }), 400
        
        created = []
        updated = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                ip = row.get('ip', '').strip()
                if not ip:
                    continue
                
                # Check if host exists
                existing = Host.query.filter_by(ip=ip, deleted_at=None).first()
                
                if existing:
                    # Update existing
                    if 'hostname' in df.columns:
                        existing.hostname = row.get('hostname', '') or None
                    if 'mac' in df.columns:
                        existing.mac = row.get('mac', '') or None
                    if 'vendor' in df.columns:
                        existing.vendor = row.get('vendor', '') or None
                    if 'os' in df.columns:
                        existing.os_type = row.get('os', '') or None
                    if 'version' in df.columns:
                        existing.os_version = row.get('version', '') or None
                    updated.append(existing)
                else:
                    # Create new
                    host = Host(
                        ip=ip,
                        hostname=row.get('hostname', '') or None if 'hostname' in df.columns else None,
                        mac=row.get('mac', '') or None if 'mac' in df.columns else None,
                        vendor=row.get('vendor', '') or None if 'vendor' in df.columns else None,
                        os_type=row.get('os', '') or None if 'os' in df.columns else None,
                        os_version=row.get('version', '') or None if 'version' in df.columns else None,
                        device_type='host',
                        is_physical=True,
                        created_by=user_id,
                    )
                    db.session.add(host)
                    created.append(host)
                    
            except Exception as e:
                errors.append({
                    'row': idx + 1,
                    'ip': row.get('ip', 'unknown'),
                    'error': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': f'Import completed: {len(created)} created, {len(updated)} updated, {len(errors)} errors',
            'data': {
                'created': len(created),
                'updated': len(updated),
                'errors': errors
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 400,
            'message': f'Failed to import CSV: {str(e)}'
        }), 400

