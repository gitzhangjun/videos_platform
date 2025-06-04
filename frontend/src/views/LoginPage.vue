<template>
  <div class="login-container">
    <div class="login-card">
      <h2>视频平台登录</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="username">用户名:</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            required 
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="password">密码:</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required 
            placeholder="请输入密码"
          />
        </div>
        <button type="submit" :disabled="loading" class="login-button">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <div v-if="message" :class="['message', { 'error': isError, 'success': !isError }]">
        {{ message }}
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import config from '../config.js';

const username = ref('');
const password = ref('');
const message = ref('');
const isError = ref(false);
const loading = ref(false);
const router = useRouter();

const login = async () => {
  if (!username.value || !password.value) {
    message.value = '请填写用户名和密码';
    isError.value = true;
    return;
  }

  loading.value = true;
  message.value = '';
  
  try {
    const response = await fetch(`${config.API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    });
    
    const data = await response.json();
    
    if (response.ok) {
      message.value = '登录成功！';
      isError.value = false;
      localStorage.setItem('user', JSON.stringify(data.user));
      setTimeout(() => {
        router.push('/');
      }, 1000);
    } else {
      message.value = data.message || '登录失败';
      isError.value = true;
    }
  } catch (error) {
    console.error('Login error:', error);
    message.value = '网络错误，请稍后重试';
    isError.value = true;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.login-card h2 {
  margin-bottom: 30px;
  color: #333;
  font-size: 1.8em;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.login-button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  margin-bottom: 20px;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.message {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-weight: 500;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.admin-hint {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #007bff;
  text-align: left;
  margin-top: 20px;
}

.admin-hint p {
  margin: 5px 0;
  color: #555;
  font-size: 14px;
}

.admin-hint p:first-child {
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}
</style>