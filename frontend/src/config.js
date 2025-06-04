// API 配置
const config = {
  // Docker环境中通过nginx代理使用相对路径，开发环境使用完整URL
  API_BASE_URL: window.location.origin.includes('8888') 
    ? ''  // Docker环境，使用相对路径通过nginx代理
    : 'http://localhost:5001',  // 开发环境
  
  // 缓存配置
  CACHE: {
    VIDEO_LIST_DURATION: 60 * 60 * 1000, // 1小时
    VIDEO_FILE_DURATION: 24 * 60 * 60 * 1000, // 24小时
    PREFIX: 'video_platform_cache_'
  },
  
  // 分页配置
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 20,
    MAX_PAGE_SIZE: 50
  },
  
  // 视频预览配置
  VIDEO_PREVIEW: {
    HOVER_DELAY: 500, // 悬停延迟（毫秒）
    PRELOAD_STRATEGY: 'none' // 预加载策略: none, metadata, auto
  },
  
  // 支持的视频格式
  SUPPORTED_VIDEO_FORMATS: [
    '.mp4', '.webm', '.ogg', '.mov', 
    '.rm', '.rmvb', '.wmv', '.avi', 
    '.3gp', '.mkv'
  ]
};

// 创建带缓存的fetch函数
export const createCachedFetch = (cacheKey, duration = config.CACHE.VIDEO_LIST_DURATION) => {
  return async (url, options = {}) => {
    const fullCacheKey = `${config.CACHE.PREFIX}${cacheKey}`;
    
    // 检查缓存
    try {
      const cached = localStorage.getItem(fullCacheKey);
      if (cached) {
        const data = JSON.parse(cached);
        const now = Date.now();
        if (now - data.timestamp < duration) {
          console.log(`Cache hit for ${cacheKey}`);
          return {
            ok: true,
            json: () => Promise.resolve(data.content)
          };
        } else {
          localStorage.removeItem(fullCacheKey);
        }
      }
    } catch (e) {
      console.warn('Cache read error:', e);
    }
    
    // 发起网络请求
    const response = await fetch(url, {
      ...options,
      headers: {
        'Cache-Control': 'max-age=3600',
        ...options.headers
      }
    });
    
    if (response.ok) {
      try {
        const data = await response.json();
        // 缓存响应
        const cacheData = {
          timestamp: Date.now(),
          content: data
        };
        localStorage.setItem(fullCacheKey, JSON.stringify(cacheData));
        console.log(`Cached response for ${cacheKey}`);
        
        return {
          ok: true,
          json: () => Promise.resolve(data)
        };
      } catch (e) {
        console.warn('Cache write error:', e);
        return response;
      }
    }
    
    return response;
  };
};

// 清除特定缓存
export const clearCache = (pattern = '') => {
  try {
    const keys = Object.keys(localStorage);
    const prefix = config.CACHE.PREFIX;
    
    keys.forEach(key => {
      if (key.startsWith(prefix) && (pattern === '' || key.includes(pattern))) {
        localStorage.removeItem(key);
      }
    });
    
    console.log(`Cleared cache with pattern: ${pattern || 'all'}`);
  } catch (e) {
    console.error('Cache clear error:', e);
  }
};

// 获取缓存统计信息
export const getCacheStats = () => {
  try {
    const keys = Object.keys(localStorage);
    const prefix = config.CACHE.PREFIX;
    const cacheKeys = keys.filter(key => key.startsWith(prefix));
    
    let totalSize = 0;
    let validCount = 0;
    const now = Date.now();
    
    cacheKeys.forEach(key => {
      const value = localStorage.getItem(key);
      if (value) {
        totalSize += value.length;
        try {
          const data = JSON.parse(value);
          if (now - data.timestamp < config.CACHE.VIDEO_LIST_DURATION) {
            validCount++;
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
    });
    
    return {
      totalKeys: cacheKeys.length,
      validKeys: validCount,
      totalSize: Math.round(totalSize / 1024), // KB
      maxAge: config.CACHE.VIDEO_LIST_DURATION / 1000 / 60 // 分钟
    };
  } catch (e) {
    console.error('Cache stats error:', e);
    return {
      totalKeys: 0,
      validKeys: 0,
      totalSize: 0,
      maxAge: 0
    };
  }
};

export default config; 