from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os
import math
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-for-sessions'
CORS(app, resources={r"/*": {"origins": ["http://localhost:8888"], "supports_credentials": True}})

# 硬编码的管理员账户
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123456'

# 配置视频上传目录
UPLOAD_FOLDER = 'videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 检查是否已登录的装饰器
def login_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# 添加缓存头的装饰器
def add_cache_headers(f):
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if hasattr(response, 'headers'):
            # 设置1小时缓存
            response.headers['Cache-Control'] = 'public, max-age=3600'
            # 只为JSON响应生成ETag，避免文件响应的问题
            try:
                if response.content_type and 'application/json' in response.content_type:
                    response.headers['ETag'] = str(hash(str(response.get_data())))
            except RuntimeError:
                # 对于文件响应，跳过ETag生成
                pass
            # 设置过期时间
            expires = datetime.utcnow() + timedelta(hours=1)
            response.headers['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response
    decorated_function.__name__ = f.__name__
    return decorated_function

# 登录路由
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    # 检查硬编码的管理员账户
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['username'] = username
        session['is_admin'] = True
        return jsonify({
            'message': 'Logged in successfully', 
            'user': {
                'username': username, 
                'is_admin': True
            }
        }), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# 登出路由
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# 获取当前用户信息
@app.route('/user_info', methods=['GET'])
@login_required
def user_info():
    return jsonify({
        'username': session.get('username'), 
        'is_admin': session.get('is_admin', False)
    }), 200

# 检查登录状态
@app.route('/check_auth', methods=['GET'])
def check_auth():
    if session.get('logged_in'):
        return jsonify({
            'authenticated': True,
            'user': {
                'username': session.get('username'),
                'is_admin': session.get('is_admin', False)
            }
        }), 200
    else:
        return jsonify({'authenticated': False}), 401

@app.route('/upload', methods=['POST'])
@login_required
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        original_filename = file.filename
        filename = original_filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 处理文件名冲突：如果文件已存在，则在文件名后追加数字
        counter = 1
        name_part, ext_part = os.path.splitext(original_filename)
        while os.path.exists(file_path):
            filename = f"{name_part}_{counter}{ext_part}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
            
        try:
            file.save(file_path)
            return jsonify({'message': 'Video uploaded successfully', 'filename': filename, 'path': f'/video/{filename}'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File upload failed'}), 500

@app.route('/videos', methods=['GET'])
@login_required
@add_cache_headers
def list_videos():
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)  # 默认每页20个视频
    
    videos = []
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        return jsonify({
            'videos': videos, 
            'total': 0,
            'page': page,
            'per_page': per_page,
            'total_pages': 0,
            'message': 'Video directory does not exist.'
        })
    
    # 获取所有视频文件
    all_files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.lower().endswith(('.mp4', '.webm', '.ogg', '.mov', '.rm', '.rmvb', '.wmv', '.avi', '.3gp', '.mkv')):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # 获取文件修改时间用于排序
            mtime = os.path.getmtime(file_path)
            all_files.append({
                'filename': filename,
                'path': f'/video/{filename}',
                'mtime': mtime,
                'size': os.path.getsize(file_path)
            })
    
    # 按修改时间倒序排列（最新的在前面）
    all_files.sort(key=lambda x: x['mtime'], reverse=True)
    
    # 计算分页
    total = len(all_files)
    total_pages = math.ceil(total / per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # 获取当前页的视频
    videos = all_files[start_idx:end_idx]
    
    # 移除不需要返回给前端的字段
    for video in videos:
        video.pop('mtime', None)
        video.pop('size', None)
    
    return jsonify({
        'videos': videos,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    })

@app.route('/video/<filename>', methods=['GET'])
@login_required
def play_video(filename):
    try:
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)
        # 为视频文件设置专门的缓存头
        response.headers['Cache-Control'] = 'public, max-age=86400'  # 24小时
        response.headers['Expires'] = (datetime.utcnow() + timedelta(days=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        # 为视频文件生成简单的ETag
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            # 使用文件修改时间和大小生成ETag
            stat = os.stat(file_path)
            etag = f'"{stat.st_mtime}-{stat.st_size}"'
            response.headers['ETag'] = etag
        return response
    except FileNotFoundError:
        return jsonify({'error': 'Video not found'}), 404

@app.route('/')
def index():
    return "Video Platform Backend is running! Please login with admin/admin123456 to access features."

if __name__ == '__main__':
    print("=" * 50)
    print("Video Platform Backend Starting...")
    print("Default Admin Account:")
    print(f"Username: {ADMIN_USERNAME}")
    print(f"Password: {ADMIN_PASSWORD}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)