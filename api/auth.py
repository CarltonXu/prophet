# Copyright (c) 2021 OnePro Cloud Ltd.
#
#   prophet is licensed under Mulan PubL v2.

"""Authentication API"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.jwt import get_current_user_id
from werkzeug.security import check_password_hash
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import io
import base64
from datetime import datetime

from models import User, db
from utils.decorators import validate_json

bp = Blueprint('auth', __name__)

# Store captcha in memory (in production, use Redis)
_captcha_store = {}


@bp.route('/captcha', methods=['GET'])
def get_captcha():
    """Generate and return captcha image"""
    # Generate random code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    # Create image
    img = Image.new('RGB', (150, 40), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except:
        font = ImageFont.load_default(size=30)
    
    draw.text((40, 0), code, fill='black', font=font)
    
    # Add more noise points (increased significantly)
    img_width, img_height = 150, 40
    for _ in range(150):
        x = random.randint(0, img_width - 1)
        y = random.randint(0, img_height - 1)
        draw.point((x, y), fill=random.choice(['gray', 'lightgray', 'darkgray']))
    
    # Add random noise lines for more interference
    for _ in range(10):
        x1 = random.randint(0, img_width)
        y1 = random.randint(0, img_height)
        x2 = random.randint(0, img_width)
        y2 = random.randint(0, img_height)
        draw.line([(x1, y1), (x2, y2)], fill=random.choice(['gray', 'lightgray']), width=1)
    
    # Add random arcs/circles for additional noise
    for _ in range(10):
        x = random.randint(0, img_width)
        y = random.randint(0, img_height)
        radius = random.randint(1, 3)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                    fill=random.choice(['gray', 'lightgray']))
    
    # Apply slight blur effect to make it more fuzzy
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Store captcha
    _captcha_store[captcha_id] = code.upper()
    
    return jsonify({
        'code': 200,
        'data': {
            'captcha_id': captcha_id,
            'image': f'data:image/png;base64,{img_str}'
        }
    })


@bp.route('/register', methods=['POST'])
@validate_json(['username', 'email', 'password', 'captcha_id', 'captcha_code'])
def register():
    """User registration"""
    data = request.json
    
    # Verify captcha
    captcha_id = data.get('captcha_id')
    captcha_code = data.get('captcha_code', '').upper()
    if captcha_id not in _captcha_store or _captcha_store[captcha_id] != captcha_code:
        return jsonify({'code': 400, 'message': 'Invalid captcha'}), 400
    
    # Remove used captcha
    del _captcha_store[captcha_id]
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'code': 400, 'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'code': 400, 'message': 'Email already exists'}), 400
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': 'Registration successful',
        'data': user.to_dict()
    }), 201


@bp.route('/login', methods=['POST'])
@validate_json(['username', 'password', 'captcha_id', 'captcha_code'])
def login():
    """User login"""
    data = request.json
    
    # Verify captcha
    captcha_id = data.get('captcha_id')
    captcha_code = data.get('captcha_code', '').upper()
    if captcha_id not in _captcha_store or _captcha_store[captcha_id] != captcha_code:
        return jsonify({'code': 400, 'message': 'Invalid captcha'}), 400
    
    # Remove used captcha
    del _captcha_store[captcha_id]
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'code': 401, 'message': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'code': 403, 'message': 'Account is disabled'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create token (identity must be a string in Flask-JWT-Extended 4.6.0+)
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'code': 200,
        'message': 'Login successful',
        'data': {
            'access_token': access_token,
            'user': user.to_dict()
        }
    })


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'code': 400, 'message': 'Invalid user ID'}), 400
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'code': 404, 'message': 'User not found'}), 404
    
    return jsonify({
        'code': 200,
        'data': user.to_dict()
    })


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout (token revocation handled client-side)"""
    return jsonify({
        'code': 200,
        'message': 'Logout successful'
    })

