# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Applications API"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.jwt import get_current_user_id
from sqlalchemy import desc

from models import Application, ApplicationHost, Host, HostRelationship, db
from utils.decorators import validate_json
from datetime import datetime

bp = Blueprint('applications', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_applications():
    """Get application list"""
    applications = Application.query.filter_by(deleted_at=None).order_by(desc(Application.created_at)).all()
    
    return jsonify({
        'code': 200,
        'data': [app.to_dict(include_hosts=True) for app in applications]
    })


@bp.route('', methods=['POST'])
@jwt_required()
@validate_json(['name'])
def create_application():
    """Create a new application"""
    data = request.json
    user_id = get_current_user_id()
    
    application = Application(
        name=data['name'],
        description=data.get('description'),
        created_by=user_id,
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Application created',
        'data': application.to_dict()
    }), 201


@bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    """Get application details"""
    application = Application.query.filter_by(id=app_id, deleted_at=None).first_or_404()
    
    return jsonify({
        'code': 200,
        'data': application.to_dict(include_hosts=True)
    })


@bp.route('/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application(app_id):
    """Update application"""
    application = Application.query.filter_by(id=app_id, deleted_at=None).first_or_404()
    data = request.json
    
    if 'name' in data:
        application.name = data['name']
    if 'description' in data:
        application.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Application updated',
        'data': application.to_dict()
    })


@bp.route('/<int:app_id>', methods=['DELETE'])
@jwt_required()
def delete_application(app_id):
    """Soft delete application"""
    application = Application.query.filter_by(id=app_id, deleted_at=None).first_or_404()
    
    application.deleted_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Application deleted'
    })


@bp.route('/<int:app_id>/hosts', methods=['POST'])
@jwt_required()
@validate_json(['host_ids'])
def add_hosts_to_application(app_id):
    """Add hosts to application"""
    application = Application.query.filter_by(id=app_id, deleted_at=None).first_or_404()
    data = request.json
    host_ids = data['host_ids']
    relationship_type = data.get('relationship_type', 'member')
    
    for host_id in host_ids:
        host = Host.query.filter_by(id=host_id, deleted_at=None).first()
        if not host:
            continue
        
        # Check if relation exists
        existing = ApplicationHost.query.filter_by(
            application_id=app_id,
            host_id=host_id
        ).first()
        
        if not existing:
            relation = ApplicationHost(
                application_id=app_id,
                host_id=host_id,
                relationship_type=relationship_type
            )
            db.session.add(relation)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Hosts added to application',
        'data': application.to_dict(include_hosts=True)
    })


@bp.route('/<int:app_id>/graph', methods=['GET'])
@jwt_required()
def get_application_graph(app_id):
    """Get application relationship graph"""
    application = Application.query.filter_by(id=app_id, deleted_at=None).first_or_404()
    
    # Get all relationships between hosts in this application
    host_ids = [h.id for h in application.hosts]
    
    relationships = HostRelationship.query.filter(
        HostRelationship.from_host_id.in_(host_ids),
        HostRelationship.to_host_id.in_(host_ids)
    ).all()
    
    return jsonify({
        'code': 200,
        'data': {
            'hosts': [h.to_dict() for h in application.hosts],
            'relationships': [r.to_dict() for r in relationships]
        }
    })


@bp.route('/<int:app_id>/relationships', methods=['POST'])
@jwt_required()
@validate_json(['from_host_id', 'to_host_id', 'relationship_type'])
def create_relationship(app_id):
    """Create host relationship"""
    application = Application.query.filter_by(id=app_id, deleted_at=None).first_or_404()
    data = request.json
    
    # Verify hosts are in application
    host_ids = [h.id for h in application.hosts]
    if data['from_host_id'] not in host_ids or data['to_host_id'] not in host_ids:
        return jsonify({
            'code': 400,
            'message': 'Both hosts must be in the application'
        }), 400
    
    # Check if relationship exists
    existing = HostRelationship.query.filter_by(
        from_host_id=data['from_host_id'],
        to_host_id=data['to_host_id']
    ).first()
    
    if existing:
        return jsonify({
            'code': 400,
            'message': 'Relationship already exists'
        }), 400
    
    relationship = HostRelationship(
        from_host_id=data['from_host_id'],
        to_host_id=data['to_host_id'],
        relationship_type=data['relationship_type'],
        description=data.get('description')
    )
    
    db.session.add(relationship)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Relationship created',
        'data': relationship.to_dict()
    }), 201

