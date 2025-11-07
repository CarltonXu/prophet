# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Data import API"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.jwt import get_current_user_id
import pandas as pd
import io

from models import Host, HostCredential, db
from utils.decorators import validate_json
from utils.encryption import encrypt_password

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
                    if 'os' in df.columns or 'os_type' in df.columns:
                        existing.os_type = row.get('os') or row.get('os_type', '') or None
                    if 'version' in df.columns or 'os_version' in df.columns:
                        existing.os_version = row.get('version') or row.get('os_version', '') or None
                    updated.append(existing)
                    
                    # Update credentials if provided
                    if 'username' in df.columns or 'password' in df.columns or 'ssh_port' in df.columns:
                        credential = HostCredential.query.filter_by(host_id=existing.id).first()
                        if not credential:
                            credential = HostCredential(host_id=existing.id)
                            db.session.add(credential)
                        
                        if 'username' in df.columns:
                            credential.username = row.get('username', '') or None
                        if 'password' in df.columns:
                            password = row.get('password', '').strip()
                            if password:
                                credential.password_encrypted = encrypt_password(password)
                        if 'ssh_port' in df.columns:
                            ssh_port = row.get('ssh_port', '')
                            credential.ssh_port = int(ssh_port) if ssh_port and str(ssh_port).isdigit() else 22
                        if 'key_path' in df.columns:
                            credential.key_path = row.get('key_path', '') or None
                else:
                    # Create new
                    host = Host(
                        ip=ip,
                        hostname=row.get('hostname', '') or None if 'hostname' in df.columns else None,
                        mac=row.get('mac', '') or None if 'mac' in df.columns else None,
                        vendor=row.get('vendor', '') or None if 'vendor' in df.columns else None,
                        os_type=(row.get('os') or row.get('os_type', '')) or None if ('os' in df.columns or 'os_type' in df.columns) else None,
                        os_version=(row.get('version') or row.get('os_version', '')) or None if ('version' in df.columns or 'os_version' in df.columns) else None,
                        device_type='host',
                        is_physical=True,
                        created_by=user_id,
                    )
                    db.session.add(host)
                    db.session.flush()  # Get host.id
                    created.append(host)
                    
                    # Create credentials if provided
                    if 'username' in df.columns or 'password' in df.columns or 'ssh_port' in df.columns:
                        credential = HostCredential(host_id=host.id)
                        if 'username' in df.columns:
                            credential.username = row.get('username', '') or None
                        if 'password' in df.columns:
                            password = row.get('password', '').strip()
                            if password:
                                credential.password_encrypted = encrypt_password(password)
                        if 'ssh_port' in df.columns:
                            ssh_port = row.get('ssh_port', '')
                            credential.ssh_port = int(ssh_port) if ssh_port and str(ssh_port).isdigit() else 22
                        if 'key_path' in df.columns:
                            credential.key_path = row.get('key_path', '') or None
                        db.session.add(credential)
                    
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

