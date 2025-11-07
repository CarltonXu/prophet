# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Hosts API"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from utils.jwt import get_current_user_id
from sqlalchemy import or_, and_
import json
import csv
import io

from models import Host, HostCredential, HostDetail, HostTag, HostTagRelation, HostRelationship, CollectionTask, db
from tasks.collector import collect_hosts_task
from utils.encryption import encrypt_password, decrypt_password
from utils.decorators import validate_json
from datetime import datetime

bp = Blueprint('hosts', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_hosts():
    """Get host list with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filters
    search = request.args.get('search')
    search_field = request.args.get('search_field', 'all')  # all, ip, hostname, mac, vendor
    os_type = request.args.get('os_type')
    device_type = request.args.get('device_type')
    is_physical = request.args.get('is_physical')
    platform_id = request.args.get('platform_id')
    tag_id = request.args.get('tag_id')
    collection_status = request.args.get('collection_status')
    source = request.args.get('source')
    
    query = Host.query.filter(Host.deleted_at == None)
    
    if search:
        if search_field == 'ip':
            query = query.filter(Host.ip.contains(search))
        elif search_field == 'hostname':
            query = query.filter(Host.hostname.contains(search))
        elif search_field == 'mac':
            query = query.filter(Host.mac.contains(search))
        elif search_field == 'vendor':
            query = query.filter(Host.vendor.contains(search))
        else:
            # Default: search all fields
            query = query.filter(
                or_(
                    Host.hostname.contains(search),
                    Host.ip.contains(search),
                    Host.mac.contains(search),
                    Host.vendor.contains(search)
                )
            )
    
    if os_type:
        query = query.filter_by(os_type=os_type)
    
    if device_type:
        query = query.filter_by(device_type=device_type)
    
    if is_physical is not None:
        query = query.filter_by(is_physical=is_physical == 'true')
    
    if platform_id:
        query = query.filter_by(virtualization_platform_id=platform_id)
    
    if tag_id:
        query = query.join(HostTagRelation).filter(HostTagRelation.tag_id == tag_id)
    
    if collection_status:
        query = query.filter_by(collection_status=collection_status)
    
    if source:
        query = query.filter_by(source=source)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'code': 200,
        'data': [host.to_dict() for host in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/<int:host_id>', methods=['GET'])
@jwt_required()
def get_host(host_id):
    """Get host details"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    
    return jsonify({
        'code': 200,
        'data': host.to_dict(include_details=True)
    })


@bp.route('', methods=['POST'])
@jwt_required()
@validate_json(['ip'])
def create_host():
    """Create a new host"""
    data = request.json
    user_id = get_current_user_id()
    
    # Check if host already exists
    existing = Host.query.filter_by(ip=data['ip'], deleted_at=None).first()
    if existing:
        return jsonify({'code': 400, 'message': 'Host with this IP already exists'}), 400
    
    host = Host(
        ip=data['ip'],
        hostname=data.get('hostname'),
        mac=data.get('mac'),
        vendor=data.get('vendor'),
        os_type=data.get('os_type'),
        os_version=data.get('os_version'),
        device_type=data.get('device_type', 'host'),
        is_physical=data.get('is_physical', True),
        virtualization_platform_id=data.get('virtualization_platform_id'),
        created_by=user_id,
    )
    
    db.session.add(host)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Host created',
        'data': host.to_dict()
    }), 201


@bp.route('/<int:host_id>', methods=['PUT'])
@jwt_required()
def update_host(host_id):
    """Update host"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    data = request.json
    
    # Update fields
    if 'hostname' in data:
        host.hostname = data['hostname']
    if 'mac' in data:
        host.mac = data['mac']
    if 'vendor' in data:
        host.vendor = data['vendor']
    if 'os_type' in data:
        host.os_type = data['os_type']
    if 'os_version' in data:
        host.os_version = data['os_version']
    if 'device_type' in data:
        host.device_type = data['device_type']
    if 'is_physical' in data:
        host.is_physical = data['is_physical']
    if 'virtualization_platform_id' in data:
        host.virtualization_platform_id = data['virtualization_platform_id']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Host updated',
        'data': host.to_dict()
    })


@bp.route('/<int:host_id>', methods=['DELETE'])
@jwt_required()
def delete_host(host_id):
    """Soft delete host"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    
    host.deleted_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Host deleted'
    })


@bp.route('/batch/delete', methods=['POST'])
@jwt_required()
@validate_json(['host_ids'])
def batch_delete_hosts():
    """Batch delete hosts"""
    data = request.json
    host_ids = data.get('host_ids', [])
    
    if not host_ids:
        return jsonify({
            'code': 400,
            'message': 'No host IDs provided'
        }), 400
    
    deleted_count = 0
    failed_ids = []
    
    for host_id in host_ids:
        try:
            host = Host.query.filter_by(id=host_id, deleted_at=None).first()
            if host:
                host.deleted_at = datetime.utcnow()
                deleted_count += 1
            else:
                failed_ids.append(host_id)
        except Exception as e:
            failed_ids.append(host_id)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': f'Deleted {deleted_count} hosts',
        'data': {
            'deleted_count': deleted_count,
            'failed_ids': failed_ids
        }
    })


@bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_create_hosts():
    """Batch create/update hosts"""
    data = request.json
    hosts_data = data.get('hosts', [])
    user_id = get_current_user_id()
    
    created = []
    updated = []
    
    for host_data in hosts_data:
        ip = host_data.get('ip')
        if not ip:
            continue
        
        existing = Host.query.filter_by(ip=ip, deleted_at=None).first()
        
        if existing:
            # Update existing
            for key, value in host_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            updated.append(existing)
        else:
            # Create new
            host = Host(
                ip=ip,
                hostname=host_data.get('hostname'),
                mac=host_data.get('mac'),
                vendor=host_data.get('vendor'),
                os_type=host_data.get('os_type'),
                os_version=host_data.get('os_version'),
                device_type=host_data.get('device_type', 'host'),
                is_physical=host_data.get('is_physical', True),
                created_by=user_id,
            )
            db.session.add(host)
            created.append(host)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': f'Created {len(created)}, updated {len(updated)} hosts',
        'data': {
            'created': [h.to_dict() for h in created],
            'updated': [h.to_dict() for h in updated]
        }
    })


@bp.route('/<int:host_id>/credentials', methods=['POST'])
@jwt_required()
@validate_json(['username'])
def set_credentials(host_id):
    """Set host credentials"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    data = request.json
    
    credential = HostCredential.query.filter_by(host_id=host_id).first()
    
    if not credential:
        credential = HostCredential(host_id=host_id)
        db.session.add(credential)
    
    credential.username = data['username']
    if 'password' in data:
        credential.password_encrypted = encrypt_password(data['password'])
    if 'ssh_port' in data:
        credential.ssh_port = data['ssh_port']
    if 'key_path' in data:
        credential.key_path = data['key_path']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Credentials updated',
        'data': credential.to_dict(decrypt_password=True)
    })


@bp.route('/<int:host_id>/credentials', methods=['GET'])
@jwt_required()
def get_credentials(host_id):
    """Get host credentials (with decrypted password)"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    credential = HostCredential.query.filter_by(host_id=host_id).first()
    
    if not credential:
        return jsonify({
            'code': 404,
            'message': 'No credentials found'
        }), 404
    
    return jsonify({
        'code': 200,
        'data': credential.to_dict(decrypt_password=True)
    })


@bp.route('/batch/collect', methods=['POST'])
@jwt_required()
@validate_json(['host_ids'])
def batch_collect():
    """Trigger batch collection"""
    data = request.json
    host_ids = data['host_ids']
    concurrent_limit = data.get('concurrent_limit')
    user_id = get_current_user_id()
    
    # Get hosts and check their source and credentials
    hosts = Host.query.filter(
        Host.id.in_(host_ids),
        Host.deleted_at == None
    ).all()
    
    if not hosts:
        return jsonify({
            'code': 404,
            'message': 'No valid hosts found'
        }), 404
    
    # Separate hosts by source
    platform_hosts = []
    scan_hosts = []
    missing_credentials = []
    
    for host in hosts:
        if host.source == 'platform':
            platform_hosts.append(host)
        elif host.source == 'scan':
            # Check if credentials exist
            credential = HostCredential.query.filter_by(host_id=host.id).first()
            if not credential or not credential.username:
                missing_credentials.append({
                    'id': host.id,
                    'ip': host.ip,
                    'hostname': host.hostname
                })
            else:
                scan_hosts.append(host)
        else:
            # For manual hosts, also check credentials
            credential = HostCredential.query.filter_by(host_id=host.id).first()
            if not credential or not credential.username:
                missing_credentials.append({
                    'id': host.id,
                    'ip': host.ip,
                    'hostname': host.hostname
                })
            else:
                scan_hosts.append(host)
    
    # If there are missing credentials, return error with list
    if missing_credentials:
        return jsonify({
            'code': 400,
            'message': 'Some hosts are missing authentication information',
            'data': {
                'missing_credentials': missing_credentials
            }
        }), 400
    
    # Handle platform hosts separately
    if platform_hosts:
        # Group by platform
        from collections import defaultdict
        platform_groups = defaultdict(list)
        for host in platform_hosts:
            platform_id = host.source_platform_id or host.virtualization_platform_id
            if platform_id:
                platform_groups[platform_id].append(host.id)
        
        # Create platform collection tasks
        platform_tasks = []
        for platform_id, p_host_ids in platform_groups.items():
            from tasks.collector import collect_platform_hosts_task
            # Create a collection task for platform hosts
            task = CollectionTask(
                concurrent_limit=1,  # Platform collection is usually sequential
                status='pending',
                created_by=user_id,
            )
            task.set_host_ids(p_host_ids)
            db.session.add(task)
            db.session.flush()
            platform_tasks.append(task)
            
            # Start async platform collection task
            collect_platform_hosts_task.delay(task.id, platform_id)
    
    # Handle scan/manual hosts with normal collection
    if scan_hosts:
        scan_host_ids = [h.id for h in scan_hosts]
        task = CollectionTask(
            concurrent_limit=concurrent_limit or 5,
            status='pending',
            created_by=user_id,
        )
        task.set_host_ids(scan_host_ids)
        db.session.add(task)
        db.session.flush()
        
        # Start async task
        collect_hosts_task.delay(task.id, concurrent_limit)
    
    db.session.commit()
    
    # Return response
    if platform_hosts and scan_hosts:
        message = f'Created {len(platform_tasks)} platform collection task(s) and 1 normal collection task'
    elif platform_hosts:
        message = f'Created {len(platform_tasks)} platform collection task(s)'
    else:
        message = 'Collection task created'
    
    return jsonify({
        'code': 200,
        'message': message,
        'data': {
            'platform_tasks': [t.to_dict() for t in platform_tasks] if platform_hosts else [],
            'normal_task': task.to_dict() if scan_hosts else None
        }
    }), 201


@bp.route('/<int:host_id>/details', methods=['GET'])
@jwt_required()
def get_host_details(host_id):
    """Get host collection details"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    
    details = HostDetail.query.filter_by(host_id=host_id).order_by(HostDetail.collected_at.desc()).all()
    
    return jsonify({
        'code': 200,
        'data': [detail.to_dict() for detail in details]
    })


@bp.route('/<int:host_id>/relationships', methods=['GET'])
@jwt_required()
def get_relationships(host_id):
    """Get host relationships"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    
    outgoing = HostRelationship.query.filter_by(from_host_id=host_id).all()
    incoming = HostRelationship.query.filter_by(to_host_id=host_id).all()
    
    return jsonify({
        'code': 200,
        'data': {
            'outgoing': [r.to_dict() for r in outgoing],
            'incoming': [r.to_dict() for r in incoming]
        }
    })


@bp.route('/batch/credentials', methods=['POST'])
@jwt_required()
@validate_json(['host_ids'])
def batch_update_credentials():
    """Batch update host credentials"""
    data = request.json
    host_ids = data['host_ids']
    credentials = data.get('credentials', {})
    
    if not credentials:
        return jsonify({
            'code': 400,
            'message': 'No credentials provided'
        }), 400
    
    updated = []
    errors = []
    
    for host_id in host_ids:
        try:
            host = Host.query.filter_by(id=host_id, deleted_at=None).first()
            if not host:
                errors.append({'host_id': host_id, 'error': 'Host not found'})
                continue
            
            credential = HostCredential.query.filter_by(host_id=host_id).first()
            if not credential:
                credential = HostCredential(host_id=host_id)
                db.session.add(credential)
            
            if 'username' in credentials:
                credential.username = credentials['username']
            if 'password' in credentials:
                credential.password_encrypted = encrypt_password(credentials['password'])
            if 'ssh_port' in credentials:
                credential.ssh_port = credentials.get('ssh_port', 22)
            if 'key_path' in credentials:
                credential.key_path = credentials.get('key_path')
            
            updated.append(host_id)
            
        except Exception as e:
            errors.append({'host_id': host_id, 'error': str(e)})
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': f'Updated credentials for {len(updated)} hosts, {len(errors)} errors',
        'data': {
            'updated': updated,
            'errors': errors
        }
    })


@bp.route('/batch/update', methods=['POST'])
@jwt_required()
@validate_json(['hosts'])
def batch_update_hosts():
    """Batch update hosts (for online table editing)"""
    data = request.json
    hosts_data = data['hosts']  # List of {id, ...fields to update}
    user_id = get_current_user_id()
    
    updated = []
    errors = []
    
    for host_data in hosts_data:
        try:
            host_id = host_data.get('id')
            if not host_id:
                errors.append({'host': host_data, 'error': 'Missing host id'})
                continue
            
            host = Host.query.filter_by(id=host_id, deleted_at=None).first()
            if not host:
                errors.append({'host': host_data, 'error': f'Host {host_id} not found'})
                continue
            
            # Update allowed fields
            allowed_fields = [
                'hostname', 'mac', 'vendor', 'os_type', 'os_version', 'os_kernel', 'os_bit',
                'boot_type', 'cpu_info', 'cpu_cores', 'memory_total', 'memory_free', 'memory_info',
                'device_type', 'is_physical', 'vt_platform', 'vt_platform_ver'
            ]
            
            for field in allowed_fields:
                if field in host_data:
                    setattr(host, field, host_data[field] or None)
            
            # Update credentials if provided
            if 'credentials' in host_data:
                cred_data = host_data['credentials']
                credential = HostCredential.query.filter_by(host_id=host_id).first()
                
                if not credential:
                    credential = HostCredential(host_id=host_id)
                    db.session.add(credential)
                
                if 'username' in cred_data:
                    credential.username = cred_data['username']
                if 'password' in cred_data:
                    credential.password_encrypted = encrypt_password(cred_data['password'])
                if 'ssh_port' in cred_data:
                    credential.ssh_port = cred_data.get('ssh_port', 22)
                if 'key_path' in cred_data:
                    credential.key_path = cred_data.get('key_path')
            
            updated.append(host)
            
        except Exception as e:
            errors.append({'host': host_data, 'error': str(e)})
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': f'Updated {len(updated)} hosts, {len(errors)} errors',
        'data': {
            'updated': [h.to_dict() for h in updated],
            'errors': errors
        }
    })


@bp.route('/tree', methods=['GET'])
@jwt_required()
def get_hosts_tree():
    """Get hosts in tree structure (platform -> ESXi -> VM)"""
    # Only get platform-sourced hosts
    hosts = Host.query.filter(
        Host.source == 'platform',
        Host.deleted_at == None
    ).all()
    
    # Separate ESXi hosts and VMs
    from collections import defaultdict
    platform_tree = defaultdict(lambda: {
        'platform_id': None,
        'platform_name': None,
        'platform_type': None,
        'esxi_hosts': defaultdict(lambda: {
            'esxi_id': None,
            'esxi_name': None,
            'esxi_ip': None,
            'vms': []
        })
    })
    
    # First pass: identify ESXi hosts and VMs
    esxi_hosts = {}  # {esxi_name: host_obj}
    vms = []  # List of (host_obj, esxi_name)
    
    for host in hosts:
        platform_id = host.source_platform_id or host.virtualization_platform_id
        if not platform_id:
            continue
        
        # Get platform info
        from models import VirtualizationPlatform
        platform = VirtualizationPlatform.query.get(platform_id)
        if not platform:
            continue
        
        # For VMware, try to identify ESXi hosts
        # ESXi hosts are typically stored with collection_method='vmware_esxi' in HostDetail
        is_esxi = False
        if platform.type == 'vmware':
            from models import HostDetail
            esxi_details = HostDetail.query.filter_by(
                host_id=host.id,
                collection_method='vmware_esxi'
            ).first()
            if esxi_details:
                is_esxi = True
        
        if is_esxi:
            esxi_name = host.hostname or host.ip
            esxi_hosts[esxi_name] = host
        else:
            # This is a VM, extract ESXi name from vendor field if stored
            esxi_name = None
            if host.vendor and host.vendor.startswith('ESXi: '):
                esxi_name = host.vendor.replace('ESXi: ', '')
            vms.append((host, esxi_name))
    
    # Group VMs by platform and ESXi
    for host, esxi_name in vms:
        platform_id = host.source_platform_id or host.virtualization_platform_id
        if not platform_id:
            continue
        
        from models import VirtualizationPlatform
        platform = VirtualizationPlatform.query.get(platform_id)
        if not platform:
            continue
        
        platform_node = platform_tree[platform_id]
        platform_node['platform_id'] = platform_id
        platform_node['platform_name'] = platform.name
        platform_node['platform_type'] = platform.type
        
        # Use ESXi name if available, otherwise group under "Unknown ESXi"
        esxi_key = esxi_name if esxi_name else 'Unknown ESXi'
        
        platform_node['esxi_hosts'][esxi_key]['esxi_name'] = esxi_key
        platform_node['esxi_hosts'][esxi_key]['vms'].append(host.to_dict())
    
    # Add ESXi hosts to tree
    for esxi_name, esxi_host in esxi_hosts.items():
        platform_id = esxi_host.source_platform_id or esxi_host.virtualization_platform_id
        if not platform_id:
            continue
        
        from models import VirtualizationPlatform
        platform = VirtualizationPlatform.query.get(platform_id)
        if not platform:
            continue
        
        platform_node = platform_tree[platform_id]
        platform_node['platform_id'] = platform_id
        platform_node['platform_name'] = platform.name
        platform_node['platform_type'] = platform.type
        
        esxi_key = esxi_name
        platform_node['esxi_hosts'][esxi_key]['esxi_id'] = esxi_host.id
        platform_node['esxi_hosts'][esxi_key]['esxi_name'] = esxi_name
        platform_node['esxi_hosts'][esxi_key]['esxi_ip'] = esxi_host.ip
    
    # Convert to list format
    result = []
    for platform_id, platform_data in platform_tree.items():
        esxi_list = []
        for esxi_key, esxi_data in platform_data['esxi_hosts'].items():
            esxi_list.append({
                'esxi_id': esxi_data.get('esxi_id'),
                'esxi_name': esxi_data['esxi_name'],
                'esxi_ip': esxi_data.get('esxi_ip'),
                'vms': esxi_data['vms']
            })
        
        result.append({
            'platform_id': platform_data['platform_id'],
            'platform_name': platform_data['platform_name'],
            'platform_type': platform_data['platform_type'],
            'esxi_hosts': esxi_list
        })
    
    return jsonify({
        'code': 200,
        'data': result
    })


@bp.route('/export/csv', methods=['GET'])
@jwt_required()
def export_hosts_csv():
    """Export hosts to CSV with credentials"""
    include_credentials = request.args.get('include_credentials', 'false').lower() == 'true'
    
    # Get filter parameters
    search = request.args.get('search')
    os_type = request.args.get('os_type')
    device_type = request.args.get('device_type')
    tag_id = request.args.get('tag_id')
    
    query = Host.query.filter(Host.deleted_at == None)
    
    if search:
        query = query.filter(
            or_(
                Host.hostname.contains(search),
                Host.ip.contains(search),
                Host.mac.contains(search)
            )
        )
    
    if os_type:
        query = query.filter_by(os_type=os_type)
    
    if device_type:
        query = query.filter_by(device_type=device_type)
    
    if tag_id:
        query = query.join(HostTagRelation).filter(HostTagRelation.tag_id == tag_id)
    
    hosts = query.all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = [
        'ID', '主机名', 'IP', 'Mac', '厂商', '操作系统类型', '操作系统版本', '操作系统内核',
        '操作系统位数', '启动方式', 'CPU信息', 'CPU核数', '内存(GB)', '剩余内存(GB)',
        '磁盘数量', '磁盘总容量(GB)', '网卡数量', '设备类型', '是否物理机', '虚拟化平台',
        '虚拟化版本', '来源', '采集状态', '最后采集时间'
    ]
    
    if include_credentials:
        header.extend(['用户名', '密码', 'SSH端口', '密钥路径'])
    
    writer.writerow(header)
    
    # Write data
    for host in hosts:
        row = [
            host.id,
            host.hostname or '',
            host.ip or '',
            host.mac or '',
            host.vendor or '',
            host.os_type or '',
            host.os_version or '',
            host.os_kernel or '',
            host.os_bit or '',
            host.boot_type or '',
            host.cpu_info or '',
            host.cpu_cores or 0,
            host.memory_total or 0,
            host.memory_free or 0,
            host.disk_count or 0,
            host.disk_total_size or 0,
            host.network_count or 0,
            host.device_type or '',
            '是' if host.is_physical else '否',
            host.vt_platform or '',
            host.vt_platform_ver or '',
            host.source or 'manual',
            host.collection_status or 'not_collected',
            host.last_collected_at.isoformat() if host.last_collected_at else '',
        ]
        
        if include_credentials:
            credential = HostCredential.query.filter_by(host_id=host.id).first()
            if credential:
                row.extend([
                    credential.username or '',
                    decrypt_password(credential.password_encrypted) if credential.password_encrypted else '',
                    credential.ssh_port or 22,
                    credential.key_path or ''
                ])
            else:
                row.extend(['', '', '', ''])
        
        writer.writerow(row)
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename=hosts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )


@bp.route('/<int:host_id>/export', methods=['GET'])
@jwt_required()
def export_host_data(host_id):
    """Export host collection data"""
    from flask import Response
    import yaml as yaml_lib
    
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    
    # Get latest detail
    detail = HostDetail.query.filter_by(host_id=host_id).order_by(HostDetail.collected_at.desc()).first()
    
    if not detail:
        return jsonify({
            'code': 404,
            'message': 'No collection data found'
        }), 404
    
    # Get export format (json or yaml)
    export_format = request.args.get('format', 'json').lower()
    
    # Prepare export data
    export_data = {
        'host': host.to_dict(include_details=True),
        'collection_detail': detail.to_dict(),
        'exported_at': datetime.utcnow().isoformat()
    }
    
    if export_format == 'yaml':
        # Export as YAML
        yaml_content = yaml_lib.dump(export_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return Response(
            yaml_content,
            mimetype='text/yaml',
            headers={
                'Content-Disposition': f'attachment; filename=host_{host.id}_{host.hostname or host.ip}_export.yaml'
            }
        )
    else:
        # Export as JSON (default)
        return Response(
            json.dumps(export_data, ensure_ascii=False, indent=2, default=str),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=host_{host.id}_{host.hostname or host.ip}_export.json'
            }
        )

