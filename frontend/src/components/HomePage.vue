<template>
  <div class="home-page">
    <div class="header-section">
      <h1>视频平台</h1>
      <div class="header-actions">
        <button @click="refreshCache" class="refresh-btn" :disabled="refreshing">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" :class="{ 'spinning': refreshing }">
            <path d="M1 4v6h6M23 20v-6h-6" stroke="currentColor" stroke-width="2"/>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" stroke="currentColor" stroke-width="2"/>
          </svg>
          {{ refreshing ? '刷新中...' : '刷新缓存' }}
        </button>
        <router-link to="/upload" class="upload-link">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/>
            <polyline points="7,10 12,5 17,10" stroke="currentColor" stroke-width="2"/>
            <line x1="12" y1="5" x2="12" y2="15" stroke="currentColor" stroke-width="2"/>
          </svg>
          上传视频
        </router-link>
      </div>
    </div>
    
    <div class="stats-section" v-if="stats.total > 0">
      <div class="stat-card">
        <div class="stat-number">{{ stats.total }}</div>
        <div class="stat-label">总视频数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.pages }}</div>
        <div class="stat-label">总页数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ formatCacheInfo() }}</div>
        <div class="stat-label">缓存状态</div>
      </div>
    </div>
    
    <VideoList ref="videoListRef" @stats-updated="updateStats" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import VideoList from './VideoList.vue';

const videoListRef = ref(null);
const refreshing = ref(false);

const stats = reactive({
  total: 0,
  pages: 0,
  cached: false
});

const updateStats = (newStats) => {
  stats.total = newStats.total || 0;
  stats.pages = newStats.total_pages || 0;
  stats.cached = newStats.cached || false;
};

const formatCacheInfo = () => {
  return stats.cached ? '已缓存' : '无缓存';
};

const refreshCache = async () => {
  if (refreshing.value) return;
  
  refreshing.value = true;
  try {
    // 清除缓存
    if (videoListRef.value) {
      videoListRef.value.clearCache();
      // 重新加载数据
      await videoListRef.value.fetchVideos();
    }
  } catch (error) {
    console.error('刷新缓存失败:', error);
  } finally {
    refreshing.value = false;
  }
};

onMounted(() => {
  // 首页不再自动加载视频列表，由VideoList组件自己控制
});
</script>

<style scoped>
.home-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.header-section h1 {
  color: #333;
  margin: 0;
  font-size: 2.2em;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.upload-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.upload-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-number {
  font-size: 2.5em;
  font-weight: 700;
  color: #333;
  margin-bottom: 5px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 1em;
  color: #666;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .home-page {
    max-width: 1200px;
  }
}

@media (max-width: 1200px) {
  .home-page {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .home-page {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .header-section h1 {
    font-size: 1.8em;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-number {
    font-size: 2em;
  }
}
</style> 