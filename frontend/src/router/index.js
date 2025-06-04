import { createRouter, createWebHashHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import UploadPage from '../views/UploadPage.vue';
import LoginPage from '../views/LoginPage.vue';
import config from '../config.js';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadPage,
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 如果访问登录页面，直接放行
  if (to.name === 'Login') {
    // 如果已经登录，重定向到首页
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const response = await fetch(`${config.API_BASE_URL}/check_auth`, {
          method: 'GET',
          credentials: 'include'
        });
        if (response.ok) {
          next('/');
          return;
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      }
    }
    next();
    return;
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const user = localStorage.getItem('user');
    if (!user) {
      next('/login');
      return;
    }

    // 验证登录状态
    try {
      const response = await fetch(`${config.API_BASE_URL}/check_auth`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        next();
      } else {
        localStorage.removeItem('user');
        next('/login');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('user');
      next('/login');
    }
  } else {
    next();
  }
});

export default router;