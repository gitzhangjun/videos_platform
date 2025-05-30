from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 添加密钥配置
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"], "supports_credentials": True}})  # 更新CORS配置

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login 配置
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 配置视频上传目录
UPLOAD_FOLDER = 'videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
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
            return jsonify({'message': 'Video uploaded successfully', 'filename': filename, 'path': f'/play/{filename}'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File upload failed'}), 500

@app.route('/videos', methods=['GET'])
def list_videos():
    videos = []
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        return jsonify({'videos': videos, 'message': 'Video directory does not exist.'})
        
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        # 支持更多视频格式
        if filename.lower().endswith(('.mp4', '.webm', '.ogg', '.mov', '.rm', '.rmvb', '.wmv', '.avi', '.3gp', '.mkv')):
            videos.append({
                'filename': filename,
                'path': f'/play/{filename}'
            })
    return jsonify({'videos': videos})

@app.route('/play/<filename>', methods=['GET'])
def play_video(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)
    except FileNotFoundError:
        return jsonify({'error': 'Video not found'}), 404

# 一个简单的首页，方便测试后端API，实际会被Vue前端取代
# 注册路由
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully. Waiting for admin approval.'}), 201

# 登录路由
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        if user.username == 'admin' or user.is_approved:
            login_user(user)
            return jsonify({'message': 'Logged in successfully', 'user': {'id': user.id, 'username': user.username, 'is_approved': user.is_approved, 'is_admin': user.is_admin}}), 200
        else:
            return jsonify({'message': 'Account not approved yet. Please wait for admin approval.'}), 403
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# 登出路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# 获取当前用户信息
@app.route('/user_info')
@login_required
def user_info():
    return jsonify({'username': current_user.username, 'is_approved': current_user.is_approved, 'is_admin': current_user.is_admin}), 200

# 管理员审批用户路由 (示例，实际应用中需要更严格的权限控制)
@app.route('/approve_user/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    # 实际应用中，这里需要验证当前用户是否是管理员
    # 为了简化，这里假设所有登录用户都可以审批，但实际应该有角色管理
    if not current_user.is_admin: # 假设只有管理员才能审批其他用户
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if user:
        user.is_approved = True
        db.session.commit()
        return jsonify({'message': f'User {user.username} approved successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

# 获取所有待审批用户
@app.route('/pending_users', methods=['GET'])
@login_required
def pending_users():
    if not current_user.is_admin: # 假设只有管理员才能查看待审批用户
        return jsonify({'message': 'Unauthorized'}), 403
    users = User.query.filter_by(is_approved=False).all()
    return jsonify([{'id': user.id, 'username': user.username} for user in users]), 200


@app.route('/')
def index():
    return "Video Platform Backend is running! Use /videos to list videos and /upload to upload." # 保持原有首页，方便测试

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # 在应用启动时创建数据库表

        # 检查并创建admin用户
        admin_username = 'admin'
        admin_password = '123456' # 请将此替换为更安全的密码
        admin_user = User.query.filter_by(username=admin_username).first()
        if not admin_user:
            admin_user = User(username=admin_username, is_approved=True, is_admin=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user '{admin_username}' created with password '{admin_password}'")
        else:
            print(f"Admin user '{admin_username}' already exists.")

    app.run(debug=True, port=5001) # 使用不同于Vue开发服务器的端口