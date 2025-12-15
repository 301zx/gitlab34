<template>
  <el-form 
    :model="form" 
    :rules="rules" 
    ref="userForm"
    label-width="80px"
  >
    <el-form-item label="用户名" prop="username">
      <el-input
        v-model="form.username"
        placeholder="请输入用户名"
        :disabled="!!user"
      />
    </el-form-item>

    <el-form-item label="邮箱" prop="email">
      <el-input
        v-model="form.email"
        placeholder="请输入邮箱"
        type="email"
      />
    </el-form-item>

    <el-form-item label="密码" prop="password" v-if="!user">
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        show-password
      />
    </el-form-item>

    <el-form-item label="角色" prop="role">
      <el-radio-group v-model="form.role">
        <el-radio label="user">普通用户</el-radio>
        <el-radio label="admin">管理员</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="状态" prop="is_active">
      <el-switch
        v-model="form.is_active"
        active-text="激活"
        inactive-text="禁用"
      />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        {{ user ? '更新' : '创建' }}
      </el-button>
      <el-button @click="handleCancel">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { userService } from '@/services/userService'

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['success', 'cancel'])

const userForm = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { 
      required: !props.user, 
      message: '请输入密码', 
      trigger: 'blur' 
    },
    { 
      min: 6, 
      message: '密码长度至少6个字符', 
      trigger: 'blur' 
    }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const handleSubmit = async () => {
  if (!userForm.value) return

  try {
    await userForm.value.validate()
    loading.value = true

    const submitData = { ...form }
    if (props.user && !submitData.password) {
      delete submitData.password // 更新时不修改密码
    }

    if (props.user) {
      await userService.updateUser(props.user.id, submitData)
      ElMessage.success('用户更新成功')
    } else {
      await userService.createUser(submitData)
      ElMessage.success('用户创建成功')
    }

    emit('success')
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}

// 监听props.user变化，填充表单数据
watch(() => props.user, (newUser) => {
  if (newUser) {
    Object.keys(form).forEach(key => {
      if (newUser[key] !== undefined) {
        form[key] = newUser[key]
      }
    })
    // 更新时不显示密码字段
    form.password = ''
  } else {
    // 重置表单
    Object.keys(form).forEach(key => {
      if (key === 'role') {
        form[key] = 'user'
      } else if (key === 'is_active') {
        form[key] = true
      } else {
        form[key] = ''
      }
    })
  }
}, { immediate: true })

// 检查用户名是否已存在
const checkUsernameExists = async (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入用户名'))
    return
  }
  
  if (props.user && props.user.username === value) {
    callback()
    return
  }
  
  try {
    // 这里需要实现用户名检查API
    // const exists = await userService.checkUsernameExists(value)
    // if (exists) {
    //   callback(new Error('用户名已存在'))
    // } else {
    //   callback()
    // }
    callback()
  } catch (error) {
    callback()
  }
}

// 检查邮箱是否已存在
const checkEmailExists = async (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入邮箱'))
    return
  }
  
  if (props.user && props.user.email === value) {
    callback()
    return
  }
  
  try {
    // 这里需要实现邮箱检查API
    // const exists = await userService.checkEmailExists(value)
    // if (exists) {
    //   callback(new Error('邮箱已存在'))
    // } else {
    //   callback()
    // }
    callback()
  } catch (error) {
    callback()
  }
}

// 更新验证规则
rules.username.push({ validator: checkUsernameExists, trigger: 'blur' })
rules.email.push({ validator: checkEmailExists, trigger: 'blur' })
</script>

<style scoped>
:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input) {
  max-width: 300px;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 20px;
}
</style>