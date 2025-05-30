<template>
  <div class="home-page">
    <header class="page-header">
      <button @click="goToUploadPage" class="upload-nav-button">&#43; 上传视频</button>
      <!-- <h1>视频中心</h1> --> <!-- Title removed to match image style -->
    </header>
    <VideoList ref="videoListRef" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import VideoList from '../components/VideoList.vue';

const videoListRef = ref(null);
const emit = defineEmits(['navigate-upload']);

const goToUploadPage = () => {
  emit('navigate-upload');
};

// 如果VideoList需要从父组件刷新，可以暴露一个方法
// defineExpose({
//   refreshVideoList: () => {
//     if (videoListRef.value) {
//       videoListRef.value.fetchVideos();
//     }
//   }
// });
</script>

<style scoped>
.home-page {
  padding: 20px;
  max-width: 1300px; /* Wider for 5 columns */
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: flex-start; /* Align button to the left */
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0; /* Lighter border */
}

/* Removed h1 styles as title is removed */

.upload-nav-button {
  padding: 10px 18px;
  background-color: #007bff; /* Standard blue */
  color: white;
  border: none;
  border-radius: 8px; /* Slightly more rounded */
  cursor: pointer;
  font-size: 1em;
  font-weight: 500;
  transition: background-color 0.25s ease, box-shadow 0.25s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.upload-nav-button:hover {
  background-color: #0069d9;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.upload-nav-button:active {
  background-color: #0056b3;
  transform: translateY(1px);
}
</style>