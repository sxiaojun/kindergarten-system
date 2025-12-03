<template>
  <div class="error-container">
    <div class="error-wrapper">
      <div class="error-code">404</div>
      <div class="error-message">抱歉，您访问的页面不存在</div>
      <div class="error-description">可能是您输入的地址有误，或者该页面已被删除</div>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/')
}
</script>

<style scoped>
.error-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.error-wrapper {
  text-align: center;
  background: #fff;
  padding: 60px 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 90%;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: #1890ff;
  line-height: 1;
  margin-bottom: 20px;
  position: relative;
}

.error-code::before {
  content: attr(data-content);
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(24, 144, 255, 0.1);
  font-size: 180px;
  z-index: -1;
}

.error-message {
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.error-description {
  font-size: 14px;
  color: #909399;
  margin-bottom: 30px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .error-wrapper {
    padding: 40px 20px;
  }
  
  .error-code {
    font-size: 80px;
  }
  
  .error-code::before {
    font-size: 120px;
  }
  
  .error-message {
    font-size: 18px;
  }
}
</style>