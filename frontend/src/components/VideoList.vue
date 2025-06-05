<template>
  <div class="video-list-container">
    <h2>视频列表</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-message">正在加载视频...</div>
    
    <!-- 错误状态 -->
    <div v-if="error" class="error-message">加载视频失败: {{ error }}</div>
    
    <!-- 空状态 -->
    <div v-if="!loading && !error && videos.length === 0" class="no-videos-message">
      暂无视频，请先上传。
    </div>

    <!-- 视频网格 -->
    <div class="video-grid" v-if="!loading && videos.length > 0">
      <div 
        class="video-item"
        v-for="video in videos"
        :key="video.filename"
      >
        <div class="video-thumbnail-wrapper" @click="playFullVideo(video)">
          <!-- 使用缩略图或视频第一帧 -->
          <img 
            v-if="video.has_thumbnail && video.thumbnail"
            :src="getVideoUrl(video.thumbnail)"
            :alt="video.filename"
            class="video-thumbnail-img"
            loading="lazy"
          />
          <!-- 降级到视频第一帧 -->
          <video 
            v-else
            class="video-first-frame-thumb"
            :src="getVideoUrl(video.path) + '#t=0.1'" 
            preload="metadata" 
            muted
            disablepictureinpicture 
            playsinline
          ></video>
          
          <!-- 播放按钮覆盖层 -->
          <div class="play-overlay">
            <div class="play-button">
              <svg width="50" height="50" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" fill="rgba(0,0,0,0.7)"/>
                <polygon points="10,8 16,12 10,16" fill="white"/>
              </svg>
            </div>
          </div>
        </div>
        
        <div class="video-info">
          <p class="video-filename" :title="video.filename">{{ video.filename }}</p>
          <div class="video-actions">
            <button @click="playFullVideo(video)" class="play-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <polygon points="5,3 19,12 5,21" fill="currentColor"/>
              </svg>
              播放
            </button>
            <button @click="confirmDelete(video)" class="delete-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14zM10 11v6M14 11v6" stroke="currentColor" stroke-width="2"/>
              </svg>
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页控件 -->
    <div v-if="pagination.total_pages > 1" class="pagination">
      <button 
        @click="loadPage(pagination.page - 1)" 
        :disabled="!pagination.has_prev"
        class="pagination-btn"
      >
        上一页
      </button>
      
      <span class="pagination-info">
        第 {{ pagination.page }} 页 / 共 {{ pagination.total_pages }} 页 
        (总共 {{ pagination.total }} 个视频)
      </span>
      
      <button 
        @click="loadPage(pagination.page + 1)" 
        :disabled="!pagination.has_next"
        class="pagination-btn"
      >
        下一页
      </button>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="deleteConfirm.show" class="delete-modal" @click.self="cancelDelete">
      <div class="delete-modal-content">
        <h3>确认删除</h3>
        <p>确定要删除视频 "{{ deleteConfirm.video?.filename }}" 吗？</p>
        <p class="delete-warning">此操作无法撤销，视频文件和缩略图将被永久删除。</p>
        <div class="delete-modal-actions">
          <button @click="cancelDelete" class="cancel-btn">取消</button>
          <button @click="executeDelete" class="confirm-delete-btn" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 美化的全屏播放模态框 -->
    <div v-if="playingVideo" class="video-modal" @click.self="closeModal">
      <div class="video-modal-content">
        <div class="video-player-wrapper">
          <video 
            ref="videoPlayer"
            :src="getVideoUrl(playingVideo.path)" 
            controls 
            autoplay 
            controlsList="nodownload"
            class="enhanced-video-player"
            @loadedmetadata="setupKeyboardControls"
            @click="focusPlayer"
            tabindex="0"
          ></video>
        </div>
        <button @click="closeModal" class="close-modal-btn">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <div class="video-title">{{ playingVideo.filename }}</div>
        <div class="video-controls-hint">
          按键提示：← 快退10秒 | → 快进10秒 | 空格 播放/暂停
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, nextTick } from 'vue';
import config from '../config.js';

const emit = defineEmits(['stats-updated']);

const videos = ref([]);
const loading = ref(true);
const error = ref(null);
const deleting = ref(false);

const playingVideo = ref(null);
const videoPlayer = ref(null);

// 删除确认对话框状态
const deleteConfirm = reactive({
  show: false,
  video: null
});

// 分页数据
const pagination = ref({
  page: 1,
  per_page: 20,
  total: 0,
  total_pages: 0,
  has_next: false,
  has_prev: false
});

// 缓存管理
const CACHE_KEY = 'video_list_cache';
const CACHE_DURATION = 60 * 60 * 1000; // 1小时

const getCachedData = (page) => {
  try {
    const cached = localStorage.getItem(`${CACHE_KEY}_page_${page}`);
    if (cached) {
      const data = JSON.parse(cached);
      const now = Date.now();
      if (now - data.timestamp < CACHE_DURATION) {
        return data.content;
      } else {
        localStorage.removeItem(`${CACHE_KEY}_page_${page}`);
      }
    }
  } catch (e) {
    console.error('Cache read error:', e);
  }
  return null;
};

const setCachedData = (page, data) => {
  try {
    const cacheData = {
      timestamp: Date.now(),
      content: data
    };
    localStorage.setItem(`${CACHE_KEY}_page_${page}`, JSON.stringify(cacheData));
  } catch (e) {
    console.error('Cache write error:', e);
  }
};

const fetchVideos = async (page = 1) => {
  // 先检查缓存
  const cachedData = getCachedData(page);
  if (cachedData) {
    console.log(`Loading page ${page} from cache`);
    videos.value = cachedData.videos;
    pagination.value = {
      page: cachedData.page,
      per_page: cachedData.per_page,
      total: cachedData.total,
      total_pages: cachedData.total_pages,
      has_next: cachedData.has_next,
      has_prev: cachedData.has_prev
    };
    loading.value = false;
    
    // 发射统计信息，标记为缓存数据
    emit('stats-updated', {
      ...pagination.value,
      cached: true
    });
    return;
  }

  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`${config.API_BASE_URL}/videos?page=${page}&per_page=20`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    
    // 缓存数据
    setCachedData(page, data);
    
    // 更新状态
    videos.value = data.videos;
    pagination.value = {
      page: data.page,
      per_page: data.per_page,
      total: data.total,
      total_pages: data.total_pages,
      has_next: data.has_next,
      has_prev: data.has_prev
    };
    
    // 发射统计信息，标记为非缓存数据
    emit('stats-updated', {
      ...pagination.value,
      cached: false
    });
  } catch (e) {
    console.error('获取视频列表失败:', e);
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

const loadPage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    fetchVideos(page);
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const getVideoUrl = (path) => {
  return `${config.API_BASE_URL}${path}`;
};

// 删除相关功能
const confirmDelete = (video) => {
  deleteConfirm.show = true;
  deleteConfirm.video = video;
};

const cancelDelete = () => {
  deleteConfirm.show = false;
  deleteConfirm.video = null;
};

const executeDelete = async () => {
  if (!deleteConfirm.video) return;
  
  deleting.value = true;
  try {
    const response = await fetch(`${config.API_BASE_URL}/video/${deleteConfirm.video.filename}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      // 删除成功，刷新列表
      await fetchVideos(pagination.value.page);
      // 清除相关页面的缓存
      clearCache();
      cancelDelete();
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Delete failed');
    }
  } catch (e) {
    console.error('删除视频失败:', e);
    error.value = `删除失败: ${e.message}`;
  } finally {
    deleting.value = false;
  }
};

// 播放相关功能
const playFullVideo = (video) => {
  playingVideo.value = video;
  // 禁用页面滚动
  document.body.style.overflow = 'hidden';
  
  // 下一帧后设置焦点和键盘控制
  nextTick(() => {
    setupKeyboardControls();
  });
};

const closeModal = () => {
  // 移除键盘事件监听
  document.removeEventListener('keydown', handleKeyboardShortcuts);
  playingVideo.value = null;
  // 恢复页面滚动
  document.body.style.overflow = 'auto';
};

const focusPlayer = () => {
  if (videoPlayer.value) {
    videoPlayer.value.focus();
  }
};

const setupKeyboardControls = () => {
  if (videoPlayer.value) {
    // 设置视频播放器为可聚焦
    videoPlayer.value.focus();
    
    // 添加键盘事件监听
    document.addEventListener('keydown', handleKeyboardShortcuts);
  }
};

const handleKeyboardShortcuts = (event) => {
  if (!videoPlayer.value) return;
  
  switch (event.key) {
    case 'ArrowLeft':
      // 快退10秒
      event.preventDefault();
      videoPlayer.value.currentTime = Math.max(0, videoPlayer.value.currentTime - 10);
      break;
    case 'ArrowRight':
      // 快进10秒
      event.preventDefault();
      videoPlayer.value.currentTime = Math.min(
        videoPlayer.value.duration, 
        videoPlayer.value.currentTime + 10
      );
      break;
    case ' ':
      // 空格键播放/暂停
      event.preventDefault();
      if (videoPlayer.value.paused) {
        videoPlayer.value.play();
      } else {
        videoPlayer.value.pause();
      }
      break;
    case 'Escape':
      // ESC键关闭模态框
      event.preventDefault();
      closeModal();
      break;
  }
};

// 清除缓存的方法
const clearCache = () => {
  try {
    for (let i = 1; i <= pagination.value.total_pages; i++) {
      localStorage.removeItem(`${CACHE_KEY}_page_${i}`);
    }
    console.log('Cache cleared');
  } catch (e) {
    console.error('Cache clear error:', e);
  }
};

// 暴露方法给父组件
defineExpose({
  fetchVideos: () => fetchVideos(1),
  clearCache
});

onMounted(() => {
  fetchVideos(1);
});
</script>

<style scoped>
.video-list-container {
  padding: 0;
}

.video-list-container h2 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  text-align: center;
  font-size: 1.5em;
}

.loading-message,
.error-message,
.no-videos-message {
  text-align: center;
  padding: 15px;
  font-size: 1em;
  color: #555;
}

.error-message {
  color: red;
}

.video-grid {
  display: grid;
  /* PC端：5列布局，平板：3-4列，手机：1-2列 */
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  padding: 0;
  margin-top: 10px;
}

/* 大屏幕 (1400px以上) - 5列 */
@media (min-width: 1400px) {
  .video-grid {
    grid-template-columns: repeat(5, 1fr);
    gap: 24px;
  }
}

/* 中大屏幕 (1200px-1399px) - 4列 */
@media (max-width: 1399px) and (min-width: 1200px) {
  .video-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
  }
}

/* 中屏幕 (992px-1199px) - 3列 */
@media (max-width: 1199px) and (min-width: 992px) {
  .video-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
  }
}

/* 平板 (768px-991px) - 2-3列 */
@media (max-width: 991px) and (min-width: 768px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

/* 手机 (最大767px) - 1-2列 */
@media (max-width: 767px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 15px;
  }
  
  .video-modal-content {
    width: 98vw;
  }
  
  .close-modal-btn {
    top: -40px;
    width: 35px;
    height: 35px;
  }
}

.video-item {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-width: 200px;
  max-width: 100%;
}

.video-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.video-thumbnail-wrapper {
  width: 100%;
  padding-top: 56.25%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
  border-radius: 12px 12px 0 0;
}

.video-thumbnail-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-first-frame-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-item:hover .play-overlay {
  opacity: 1;
}

.play-button {
  transform: scale(0.8);
  transition: transform 0.3s ease;
}

.video-item:hover .play-button {
  transform: scale(1);
}

.video-info {
  padding: 15px;
  background: white;
}

.video-filename {
  text-align: left;
  font-size: 0.95em;
  color: #333;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.8em;
  margin: 0 0 10px 0;
}

.video-actions {
  display: flex;
  gap: 8px;
  justify-content: space-between;
}

.play-btn,
.delete-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 500;
  transition: all 0.3s ease;
}

.play-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex: 1;
}

.play-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.delete-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
  color: white;
  flex: 0 0 auto;
}

.delete-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin: 40px 0 20px 0;
  padding: 20px;
}

.pagination-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.pagination-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.pagination-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.pagination-info {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

/* 美化的视频播放模态框 */
.video-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(10px);
}

.video-modal-content {
  position: relative;
  width: 95vw;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.video-player-wrapper {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}

.enhanced-video-player {
  width: 100%;
  height: auto;
  display: block;
  outline: none;
  background: #000;
}

.close-modal-btn {
  position: absolute;
  top: -50px;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.close-modal-btn:hover {
  background: white;
  transform: scale(1.1);
}

.video-title {
  color: white;
  text-align: center;
  margin-top: 20px;
  font-size: 1.2em;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.video-controls-hint {
  color: white;
  text-align: center;
  margin-top: 10px;
  font-size: 0.8em;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

/* 删除确认对话框 */
.delete-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  backdrop-filter: blur(5px);
}

.delete-modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.delete-modal-content h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.3em;
}

.delete-modal-content p {
  margin: 10px 0;
  color: #666;
  line-height: 1.5;
}

.delete-warning {
  color: #ff6b6b !important;
  font-weight: 500;
}

.delete-modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  justify-content: flex-end;
}

.cancel-btn,
.confirm-delete-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
}

.cancel-btn:hover {
  background: #e9ecef;
}

.confirm-delete-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
  color: white;
}

.confirm-delete-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
}

.confirm-delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>