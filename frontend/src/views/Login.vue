<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h2>图书管理系统 - 登录</h2>
          <p>欢迎回来，请登录您的账户</p>
        </div>
      </template>
      
      <el-form 
        :model="form" 
        :rules="rules" 
        ref="loginForm"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="login">
          <el-input
            v-model="form.login"
            placeholder="用户名或邮箱"
            prefix-icon="User"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-links">
        <router-link to="/register">没有账户？立即注册</router-link>
        <span class="divider">|</span>
        <a href="#" @click.prevent="showDemoAccounts">演示账户</a>
      </div>
    </el-card>

    <!-- 演示账户对话框 -->
    <el-dialog
      v-model="showDemoDialog"
      title="演示账户"
      width="400px"
    >
      <div class="demo-accounts">
        <div class="demo-account">
          <strong>管理员账户：</strong>
          <p>用户名: admin</p>
          <p>密码: admin123</p>
          <el-button 
            type="primary" 
            size="small"
            @click="fillAdminCredentials"
          >
            使用此账户
          </el-button>
        </div>
        <div class="demo-account">
          <strong>普通用户：</strong>
          <p>用户名: user</p>
          <p>密码: user123</p>
          <el-button 
            type="success" 
            size="small"
            @click="fillUserCredentials"
          >
            使用此账户
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = ref()
const loading = ref(false)
const rememberMe = ref(false)
const showDemoDialog = ref(false)

const form = reactive({
  login: '',
  password: ''
})

const rules = {
  login: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginForm.value) return
  
  try {
    // 表单验证
    await loginForm.value.validate()
    loading.value = true

    // 调用登录接口
    await authStore.login(form)
    
    ElMessage.success('登录成功！')
    
    // 根据用户角色跳转到不同页面
    if (authStore.isAdmin) {
      router.push('/admin')
    } else {
      router.push('/')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.response?.data?.error || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

const showDemoAccounts = () => {
  showDemoDialog.value = true
}

const fillAdminCredentials = () => {
  form.login = 'admin'
  form.password = 'admin123'
  showDemoDialog.value = false
}

const fillUserCredentials = () => {
  form.login = 'user'
  form.password = 'user123'
  showDemoDialog.value = false
}

// 检查是否已登录
onMounted(() => {
  if (authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      router.push('/admin')
    } else {
      router.push('/')
    }
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
}

.login-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.login-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.login-links {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.login-links a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}

.login-links a:hover {
  text-decoration: underline;
}

.divider {
  margin: 0 12px;
  color: #dcdfe6;
}

.demo-accounts {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.demo-account {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: #fafafa;
}

.demo-account p {
  margin: 5px 0;
  font-family: monospace;
}
</style>