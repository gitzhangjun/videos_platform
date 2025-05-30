<template>
  <div class="video-list-container">
    <h2>视频列表</h2>
    <div v-if="loading" class="loading-message">正在加载视频...</div>
    <div v-if="error" class="error-message">加载视频失败: {{ error }}</div>
    <div v-if="!loading && !error && videos.length === 0" class="no-videos-message">
      暂无视频，请先上传。
    </div>
    <div class="video-grid" v-if="!loading && videos.length > 0">
      <div 
        class="video-item"
        v-for="video in videos"
        :key="video.filename"
        @mouseenter="startPreview(video, $event)"
        @mouseleave="stopPreview(video, $event)"
        @click="playFullVideo(video)"
      >
        <div class="video-thumbnail-wrapper">
          <!-- 预览播放器 -->
          <video 
            :ref="el => videoRefs[video.filename] = el"
            class="video-preview"
            muted
            loop
            preload="metadata"
            :src="getVideoUrl(video.path)"
            v-show="video.isPreviewing"          ></video>
          <!-- 静态视频帧作为缩略图 -->
          <div class="video-static-thumbnail" v-show="!video.isPreviewing">
            <video 
              class="video-first-frame-thumb"
              :src="getVideoUrl(video.path) + '#t=0.1'" 
              preload="metadata" 
              muted
              disablepictureinpicture 
              playsinline
            ></video>
          </div>
        </div>
        <p class="video-filename">{{ video.filename }}</p>
      </div>
    </div>

    <!-- 全屏播放模态框 -->
    <div v-if="playingVideo" class="video-modal" @click.self="closeModal">
      <div class="video-modal-content">
        <video :src="getVideoUrl(playingVideo.path)" controls autoplay controlsList="nodownload"></video>
        <button @click="closeModal" class="close-modal-btn">&times;</button>
        <p>{{ playingVideo.filename }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';

const videos = ref([]);
const loading = ref(true);
const error = ref(null);
const videoRefs = reactive({}); // To store refs for each video element for preview
let previewTimeout = null;

const playingVideo = ref(null); // For full screen playback

const fetchVideos = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch('http://localhost:5001/videos');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    // Add isPreviewing state to each video object for hover preview control
    videos.value = data.videos.map(v => ({ ...v, isPreviewing: false }));
  } catch (e) {
    console.error('获取视频列表失败:', e);
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

const getVideoUrl = (path) => {
  return `http://localhost:5001${path}`;
};

const startPreview = (video, event) => {
  clearTimeout(previewTimeout); // Clear any existing timeout
  previewTimeout = setTimeout(() => {
    const videoElement = videoRefs[video.filename];
    if (videoElement) {
      video.isPreviewing = true;
      videoElement.currentTime = 0; // Start from the beginning
      videoElement.play().catch(err => {
        console.warn('Preview play failed:', err);
        video.isPreviewing = false; // Revert if play fails
      });
    }
  }, 300); // Delay before starting preview
};

const stopPreview = (video, event) => {
  clearTimeout(previewTimeout);
  const videoElement = videoRefs[video.filename];
  if (videoElement && video.isPreviewing) {
    videoElement.pause();
    videoElement.currentTime = 0; // Reset to beginning
    video.isPreviewing = false;
  }
};

const playFullVideo = (video) => {
  playingVideo.value = video;
};

const closeModal = () => {
  playingVideo.value = null;
};

// Expose fetchVideos so parent can call it
defineExpose({
  fetchVideos
});

onMounted(() => {
  fetchVideos();
});

</script>

<style scoped>
.video-list-container {
  padding: 20px;
}

.video-list-container h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.loading-message,
.error-message,
.no-videos-message {
  text-align: center;
  padding: 20px;
  font-size: 1.1em;
  color: #555;
}

.error-message {
  color: red;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* Always 5 columns on larger screens */
  gap: 20px;
  padding: 0;
}

/* Responsive adjustments for fewer columns */
@media (max-width: 1300px) { /* Matches HomePage max-width */
  .video-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1024px) {
  .video-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}

@media (max-width: 576px) {
  .video-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
}

@media (max-width: 1200px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(calc(25% - 15px), 1fr)); /* 4 items */
  }
}

@media (max-width: 992px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(calc(33.33% - 14px), 1fr)); /* 3 items */
  }
}

@media (max-width: 768px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(calc(50% - 10px), 1fr)); /* 2 items */
  }
}

@media (max-width: 576px) {
  .video-grid {
    grid-template-columns: 1fr; /* 1 item */
    gap: 15px;
  }
}

.video-item {
  border: none; /* Remove border, rely on shadow and spacing */
  border-radius: 8px; /* Match image style more closely */
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  background-color: #fff; /* Keep white background for card */
  display: flex;
  flex-direction: column;
  /* box-shadow: 0 2px 5px rgba(0,0,0,0.08); Removed for a cleaner look, hover will add shadow */
}

.video-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.video-thumbnail-wrapper {
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
  background-color: #f0f2f5; /* Lighter placeholder, closer to image */
  position: relative;
  overflow: hidden;
  border-radius: 8px; /* Rounded corners for the thumbnail itself */
}

.video-preview,
.video-static-thumbnail video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-static-thumbnail {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  /* background-color: #e9ecef; */ /* 移除背景色，让内部video标签填充 */
  border-radius: inherit;
  overflow: hidden; /* 确保内部video不会溢出圆角 */
}

.video-first-frame-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 确保视频帧覆盖整个区域 */
  pointer-events: none; /* 防止对静态缩略图视频元素的意外交互 */
}

/* 如果之前有针对SVG的特定样式，确保它们不会影响新的空div */

.video-filename {
  padding: 10px 0 4px 0; /* Adjust padding, no side padding as it's full width */
  text-align: left;
  font-size: 0.9em; /* Slightly smaller to match image */
  color: #18191c; /* Darker text, common for titles */
  background-color: transparent; /* No background for filename area */
  border-top: none; /* No border */
  white-space: normal; /* Allow wrapping for longer titles */
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500; /* Keep medium weight */
  line-height: 1.4;
  /* Simulate two-line clamp for title */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: calc(0.9em * 1.4 * 2); /* Reserve space for two lines */
}

/* Add meta info style similar to image (author, date) - not in current data model */
/* Example for future use if data is available:
.video-meta {
  font-size: 0.8em;
  color: #909399;
  padding: 0 0 8px 0;
}
*/

/* Full screen video modal */
.video-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.video-modal-content {
  position: relative;
  background-color: #000;
  padding: 20px;
  border-radius: 8px;
  max-width: 90vw;
  max-height: 85vh;
}

.video-modal-content video {
  display: block;
  width: 100%; /* Ensure video takes full width of modal content */
  max-height: calc(85vh - 80px); /* Adjust for padding and text */
  outline: none;
  border-radius: 4px; /* Slight radius for the video player itself */
}

.video-modal-content p {
  color: white;
  text-align: center;
  margin-top: 10px;
}

.close-modal-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background-color: white;
  color: #333;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  font-size: 20px;
  line-height: 30px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
</style>