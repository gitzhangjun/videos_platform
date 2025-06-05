<template>
  <div class="video-upload">
    <h2>上传新视频</h2>
    <input type="file" @change="handleFileChange" accept="video/*" ref="fileInput" />
    <button @click="uploadVideo" :disabled="!selectedFile || uploading">
      {{ uploading ? '上传中...' : '上传' }}
    </button>
    <p v-if="uploadMessage" :class="{ 'error-message': uploadError, 'success-message': !uploadError }">
      {{ uploadMessage }}
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import config from '../config.js';

const selectedFile = ref(null);
const uploading = ref(false);
const uploadMessage = ref('');
const uploadError = ref(false);
const fileInput = ref(null); // Ref for the file input element

const emit = defineEmits(['upload-success', 'video-uploaded']);

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
  uploadMessage.value = ''; // Clear previous message
  uploadError.value = false;
};

const uploadVideo = async () => {
  if (!selectedFile.value) {
    uploadMessage.value = '请先选择一个视频文件。';
    uploadError.value = true;
    return;
  }

  uploading.value = true;
  uploadMessage.value = '';
  uploadError.value = false;

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const response = await fetch(`${config.API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      uploadMessage.value = `视频 '${selectedFile.value.name}' 上传成功! 文件名: ${result.filename}`;
      uploadError.value = false;
      selectedFile.value = null; // Reset file input
      if (fileInput.value) {
        fileInput.value.value = ''; // Clear the file input visually
      }
      emit('upload-success'); // 通知父组件上传成功

      // 根据缩略图生成结果显示不同的消息
      if (result.thumbnail_generated) {
        uploadMessage.value += `，缩略图已生成`;
      } else {
        uploadMessage.value += `，但缩略图生成失败`;
        if (result.warning) {
          console.warn(result.warning);
        }
      }

      // 通知父组件刷新视频列表
      emit('video-uploaded');
    } else {
      const errorData = await response.json();
      uploadMessage.value = `上传失败: ${errorData.error || '未知错误'}`;
      uploadError.value = true;
    }
  } catch (error) {
    console.error('上传错误:', error);
    uploadMessage.value = `上传出错: ${error.message}`;
    uploadError.value = true;
  } finally {
    uploading.value = false;
  }
};
</script>

<style scoped>
.video-upload {
  margin-bottom: 20px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.video-upload h2 {
  margin-top: 0;
}

.video-upload input[type="file"] {
  margin-right: 10px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.video-upload button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.video-upload button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.video-upload button:hover:not(:disabled) {
  background-color: #0056b3;
}

.error-message {
  color: red;
  margin-top: 10px;
}

.success-message {
  color: green;
  margin-top: 10px;
}
</style>