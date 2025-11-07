# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Tags API"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from models import HostTag, HostTagRelation, Host, db
from utils.decorators import validate_json

bp = Blueprint('tags', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_tags():
    """Get all tags"""
    tags = HostTag.query.order_by(HostTag.name).all()
    
    return jsonify({
        'code': 200,
        'data': [tag.to_dict() for tag in tags]
    })


@bp.route('', methods=['POST'])
@jwt_required()
@validate_json(['name'])
def create_tag():
    """Create a new tag"""
    data = request.json
    
    # Check if tag exists
    existing = HostTag.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'code': 400, 'message': 'Tag already exists'}), 400
    
    tag = HostTag(
        name=data['name'],
        color=data.get('color', '#3B82F6'),
        description=data.get('description'),
    )
    
    db.session.add(tag)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Tag created',
        'data': tag.to_dict()
    }), 201


@bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """Update tag"""
    tag = HostTag.query.get_or_404(tag_id)
    data = request.json
    
    if 'name' in data:
        tag.name = data['name']
    if 'color' in data:
        tag.color = data['color']
    if 'description' in data:
        tag.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Tag updated',
        'data': tag.to_dict()
    })


@bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """Delete tag"""
    tag = HostTag.query.get_or_404(tag_id)
    
    # Remove all relations
    HostTagRelation.query.filter_by(tag_id=tag_id).delete()
    
    db.session.delete(tag)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Tag deleted'
    })


@bp.route('/hosts/<int:host_id>', methods=['POST'])
@jwt_required()
@validate_json(['tag_ids'])
def add_host_tags(host_id):
    """Add tags to host"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    data = request.json
    tag_ids = data['tag_ids']
    
    for tag_id in tag_ids:
        # Check if relation exists
        existing = HostTagRelation.query.filter_by(host_id=host_id, tag_id=tag_id).first()
        if not existing:
            relation = HostTagRelation(host_id=host_id, tag_id=tag_id)
            db.session.add(relation)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Tags added',
        'data': host.to_dict()
    })


@bp.route('/hosts/<int:host_id>/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_host_tag(host_id, tag_id):
    """Remove tag from host"""
    host = Host.query.filter_by(id=host_id, deleted_at=None).first_or_404()
    
    relation = HostTagRelation.query.filter_by(host_id=host_id, tag_id=tag_id).first()
    if relation:
        db.session.delete(relation)
        db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Tag removed'
    })

