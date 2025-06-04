<template>
  <div class="upload-page">
    <header class="page-header">
      <button @click="goHome" class="back-button">&larr; 返回首页</button>
      <h1>上传新视频</h1>
    </header>
    <div class="upload-form-container">
      <input 
        type="file" 
        @change="handleFileChange" 
        accept=".mp4,.webm,.ogg,.mov,.rm,.rmvb,.wmv,.avi,.3gp,.mkv,video/*" 
        ref="fileInput" 
        multiple 
      />
      <div class="supported-formats">
        <p>支持的视频格式: MP4, WEBM, OGG, MOV, RM, RMVB, WMV, AVI, 3GP, MKV</p>
      </div>
      <button @click="uploadVideos" :disabled="selectedFiles.length === 0 || uploading" class="upload-button">
        {{ uploading ? '上传中...' : '开始上传所选视频' }}
      </button>
      <div v-if="uploadMessages.length > 0" class="messages-container">
        <p v-for="(msg, index) in uploadMessages" :key="index" :class="['message', { 'error-message': msg.error, 'success-message': !msg.error }]">
          {{ msg.text }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import config from '../config.js';

const selectedFiles = ref([]);
const uploading = ref(false);
const uploadMessages = ref([]); // 用于存储每个文件的上传消息
const fileInput = ref(null);
const router = useRouter();

const emit = defineEmits(['upload-success']);

const handleFileChange = (event) => {
  selectedFiles.value = Array.from(event.target.files);
  uploadMessages.value = []; // 清空之前的消息
};

const uploadVideos = async () => {
  if (selectedFiles.value.length === 0) {
    uploadMessages.value = [{ text: '请先选择视频文件。', error: true }];
    return;
  }

  uploading.value = true;
  uploadMessages.value = []; // 开始上传前清空消息
  let allUploadsSuccessful = true;

  for (const file of selectedFiles.value) {
    const formData = new FormData();
    formData.append('file', file);
    
    // 为每个文件显示开始上传的消息
    uploadMessages.value.push({ text: `开始上传 '${file.name}'...`, error: false });

    try {
      const response = await fetch(`${config.API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      const currentFileMessageIndex = uploadMessages.value.length -1; // 获取当前文件消息的索引

      if (response.ok) {
        uploadMessages.value.splice(currentFileMessageIndex, 1, { 
          text: `视频 '${file.name}' 上传成功! 文件名: ${data.filename}`,
          error: false 
        });
      } else {
        uploadMessages.value.splice(currentFileMessageIndex, 1, { 
          text: `视频 '${file.name}' 上传失败: ${data.error || '未知错误'}`,
          error: true 
        });
        allUploadsSuccessful = false;
      }
    } catch (error) {
      console.error(`上传 '${file.name}' 错误:`, error);
      const currentFileMessageIndex = uploadMessages.value.length -1;
      uploadMessages.value.splice(currentFileMessageIndex, 1, { 
        text: `视频 '${file.name}' 上传出错: ${error.message}`,
        error: true 
      });
      allUploadsSuccessful = false;
    }
  }

  uploading.value = false;
  if (allUploadsSuccessful) {
    selectedFiles.value = [];
    if (fileInput.value) {
      fileInput.value.value = ''; // 重置文件输入
    }
    emit('upload-success'); // 所有文件成功后触发
    // 可以添加一个总的成功消息
    uploadMessages.value.push({ text: '所有选定视频均已处理完毕。', error: false });
  } else {
     uploadMessages.value.push({ text: '部分视频上传失败，请检查上述信息。', error: true });
  }
};

const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.upload-page {
  padding: 20px;
  max-width: 800px;
  margin: 20px auto;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.page-header h1 {
  margin: 0 0 0 20px;
  font-size: 1.8em;
  color: #333;
  flex-grow: 1;
  text-align: center;
}

.back-button {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  padding: 10px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95em;
  transition: background-color 0.2s, box-shadow 0.2s;
}

.back-button:hover {
  background-color: #e0e0e0;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.upload-form-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px;
}

.upload-form-container input[type="file"] {
  border: 2px dashed #007bff;
  padding: 20px;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  max-width: 400px;
  text-align: center;
  color: #555;
}

.upload-form-container input[type="file"]::file-selector-button {
  margin-right: 10px;
  padding: 8px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.upload-button {
  padding: 12px 25px;
  background-color: #28a745; /* Green for go */
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: bold;
  transition: background-color 0.3s ease, transform 0.1s ease;
}

.upload-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.upload-button:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-1px);
}

.messages-container {
  margin-top: 15px;
  width: 100%;
  max-width: 500px; /* 稍微加宽以容纳更长的文件名 */
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message {
  padding: 10px 15px;
  border-radius: 4px;
  text-align: left; /* 左对齐消息文本 */
  word-break: break-word; /* 防止长文件名破坏布局 */
}

.error-message {
  color: #D8000C;
  background-color: #FFD2D2;
  border: 1px solid #D8000C;
}

.success-message {
  color: #4F8A10;
  background-color: #DFF2BF;
  border: 1px solid #4F8A10;
}

.supported-formats {
  margin-top: 10px;
  font-size: 0.85em;
  color: #666;
  text-align: center;
  width: 100%;
  max-width: 400px;
}
</style>