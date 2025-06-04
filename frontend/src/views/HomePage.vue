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
import { useRouter } from 'vue-router';

const videoListRef = ref(null);
const router = useRouter();

const goToUploadPage = () => {
  router.push('/upload');
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
  padding: 5px 10px; /* 减少上下边距 */
}

.page-header {
  display: flex;
  justify-content: flex-start; /* Align button to the left */
  align-items: center;
  margin-bottom: 15px; /* 减少底部边距 */
  padding-bottom: 10px; /* 减少底部内边距 */
  border-bottom: 1px solid #f0f0f0; /* Lighter border */
}

/* Removed h1 styles as title is removed */

.upload-nav-button {
  padding: 8px 15px; /* 减少按钮大小 */
  background-color: #007bff; /* Standard blue */
  color: white;
  border: none;
  border-radius: 6px; /* Slightly more rounded */
  cursor: pointer;
  font-size: 0.9em; /* 减少字体大小 */
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