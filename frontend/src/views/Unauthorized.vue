<template>
  <div class="unauthorized">
    <div class="unauthorized-content">
      <div class="error-icon">
        <el-icon><Lock /></el-icon>
      </div>
      <h1 class="error-title">权限不足</h1>
      <p class="error-description">抱歉，您没有权限访问此页面。</p>
      <div class="action-buttons">
        <el-button type="primary" @click="$router.push('/')">
          <el-icon><Home /></el-icon>
          返回首页
        </el-button>
        <el-button @click="$router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回上一页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Lock, Home, ArrowLeft } from '@element-plus/icons-vue'
</script>

<style scoped>
.unauthorized {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
  padding: 20px;
}

.unauthorized-content {
  text-align: center;
  background: white;
  padding: 60px 40px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}

.error-icon {
  font-size: 80px;
  color: #ff6b6b;
  margin-bottom: 20px;
}

.error-title {
  font-size: 32px;
  color: #303133;
  margin-bottom: 16px;
}

.error-description {
  font-size: 16px;
  color: #606266;
  margin-bottom: 30px;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .error-icon {
    font-size: 60px;
  }
  
  .error-title {
    font-size: 24px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}
</style>