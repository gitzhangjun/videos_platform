<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import config from './config.js';

const router = useRouter();
const isLoggedIn = ref(false);
const currentUser = ref(null);

const checkLoginStatus = () => {
  const user = localStorage.getItem('user');
  if (user) {
    try {
      currentUser.value = JSON.parse(user);
      isLoggedIn.value = true;
    } catch (error) {
      console.error('Error parsing user data:', error);
      localStorage.removeItem('user');
      isLoggedIn.value = false;
    }
  } else {
    isLoggedIn.value = false;
    currentUser.value = null;
  }
};

const logout = async () => {
  try {
    await fetch(`${config.API_BASE_URL}/logout`, {
      method: 'POST',
      credentials: 'include'
    });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    localStorage.removeItem('user');
    isLoggedIn.value = false;
    currentUser.value = null;
    router.push('/login');
  }
};

onMounted(() => {
  checkLoginStatus();
  // 监听localStorage变化
  window.addEventListener('storage', checkLoginStatus);
  
  // 监听路由变化来更新登录状态
  router.afterEach(() => {
    checkLoginStatus();
  });
});
</script>

<template>
  <div id="app">
    <nav v-if="isLoggedIn">
      <div class="nav-left">
        <router-link to="/">首页</router-link>
        <router-link to="/upload">上传视频</router-link>
      </div>
      <div class="nav-right">
        <span class="user-info">欢迎, {{ currentUser?.username }}</span>
        <button @click="logout" class="logout-btn">登出</button>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 0;
}

.nav-left {
  display: flex;
  gap: 20px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

nav a:hover {
  background-color: #e9ecef;
}

nav a.router-link-exact-active {
  color: #42b983;
  background-color: #e8f5e8;
}

.user-info {
  color: #666;
  font-size: 14px;
}

.logout-btn {
  padding: 6px 12px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.logout-btn:hover {
  background-color: #c82333;
}

/* 登录页面不显示margin-top */
.login-container {
  margin-top: 0 !important;
}

/* 其他页面保持原有的margin-top */
.home-page,
.upload-page {
  margin-top: 0;
}
</style>
