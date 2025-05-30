<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = ref(false);

const checkLoginStatus = () => {
  isLoggedIn.value = !!localStorage.getItem('user');
};

const logout = () => {
  localStorage.removeItem('user');
  isLoggedIn.value = false;
  router.push('/login');
};

onMounted(() => {
  checkLoginStatus();
  // 监听localStorage变化，以便在其他页面登录/登出时更新状态
  window.addEventListener('storage', checkLoginStatus);
});
</script>

<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/upload">Upload</router-link> |
      <template v-if="!isLoggedIn">
        <router-link to="/login">Login</router-link> |
        <router-link to="/register">Register</router-link>
      </template>
      <template v-else>
        <a href="#" @click.prevent="logout">Logout</a>
      </template>
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
  margin-top: 60px;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
