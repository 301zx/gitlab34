<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="profile-header">
          <h2>个人中心</h2>
          <p>管理您的个人信息和账户设置</p>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="info">
          <el-form 
            :model="profileForm" 
            :rules="profileRules" 
            ref="profileForm"
            label-width="100px"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" type="email" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="loading">
                更新信息
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 修改密码 -->
        <el-tab-pane label="修改密码" name="password">
          <el-form 
            :model="passwordForm" 
            :rules="passwordRules" 
            ref="passwordForm"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input 
                v-model="passwordForm.currentPassword" 
                type="password" 
                show-password 
              />
            </el-form-item>

            <el-form-item label="新密码" prop="newPassword">
              <el-input 
                v-model="passwordForm.newPassword" 
                type="password" 
                show-password 
              />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input 
                v-model="passwordForm.confirmPassword" 
                type="password" 
                show-password 
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="loading">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 我的借阅 -->
        <el-tab-pane label="我的借阅" name="borrows">
          <div class="borrows-section">
            <el-tabs v-model="borrowStatus">
              <el-tab-pane label="当前借阅" name="current">
                <BorrowList :status="['borrowed']" />
              </el-tab-pane>
              <el-tab-pane label="借阅历史" name="history">
                <BorrowList :status="['returned']" />
              </el-tab-pane>
              <el-tab-pane label="逾期记录" name="overdue">
                <BorrowList :status="['overdue']" />
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { userService } from '@/services/userService'
import BorrowList from '@/components/BorrowList.vue'

const authStore = useAuthStore()
const activeTab = ref('info')
const borrowStatus = ref('current')
const loading = ref(false)

const profileForm = reactive({
  username: '',
  email: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户信息
const loadUserProfile = () => {
  if (authStore.user) {
    profileForm.username = authStore.user.username
    profileForm.email = authStore.user.email
  }
}

const updateProfile = async () => {
  try {
    loading.value = true
    await userService.updateProfile({
      username: profileForm.username,
      email: profileForm.email
    })
    
    // 更新store中的用户信息
    authStore.user.username = profileForm.username
    authStore.user.email = profileForm.email
    
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    ElMessage.error('更新失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const changePassword = async () => {
  try {
    loading.value = true
    await userService.changePassword({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    })
    
    // 重置表单
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    
    ElMessage.success('密码修改成功')
  } catch (error) {
    ElMessage.error('密码修改失败，请检查当前密码是否正确')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-header {
  text-align: center;
}

.profile-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.profile-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.borrows-section {
  margin-top: 20px;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}
</style>