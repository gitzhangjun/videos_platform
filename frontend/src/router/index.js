import { createRouter, createWebHashHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import UploadPage from '../views/UploadPage.vue';
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadPage,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// 导航守卫
router.beforeEach(async (to, from, next) => {
  const publicPages = ['/login', '/register']; // 不需要认证的页面
  const authRequired = !publicPages.includes(to.path);
  const loggedIn = localStorage.getItem('user'); // 假设登录状态存储在localStorage中

  if (authRequired && !loggedIn) {
    next('/login'); // 未登录且需要认证，重定向到登录页
  } else {
    next(); // 继续访问
  }
});

export default router;