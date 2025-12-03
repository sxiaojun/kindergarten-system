<template>
  <div class="error-container">
    <div class="error-wrapper">
      <div class="error-icon">
        <el-icon><WarningFilled /></el-icon>
      </div>
      <div class="error-code">403</div>
      <div class="error-message">抱歉，您没有权限访问此页面</div>
      <div class="error-description">请联系管理员获取相应权限或返回首页</div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { WarningFilled } from '@element-plus/icons-vue'

const router = useRouter()

function goHome() {
  router.push('/')
}

function goBack() {
  router.back()
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

.error-icon {
  font-size: 64px;
  color: #e6a23c;
  margin-bottom: 20px;
}

.error-code {
  font-size: 80px;
  font-weight: 700;
  color: #e6a23c;
  line-height: 1;
  margin-bottom: 20px;
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

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .error-wrapper {
    padding: 40px 20px;
  }
  
  .error-icon {
    font-size: 48px;
  }
  
  .error-code {
    font-size: 60px;
  }
  
  .error-message {
    font-size: 18px;
  }
  
  .error-actions {
    flex-direction: column;
  }
}
</style>