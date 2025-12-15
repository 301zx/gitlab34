<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showAddUserDialog = true">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-input
        v-model="filters.search"
        placeholder="搜索用户名或邮箱"
        class="search-input"
        @input="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>

      <el-select
        v-model="filters.role"
        placeholder="选择角色"
        clearable
        @change="handleFilterChange"
      >
        <el-option label="管理员" value="admin" />
        <el-option label="普通用户" value="user" />
      </el-select>

      <el-select
        v-model="filters.status"
        placeholder="选择状态"
        clearable
        @change="handleFilterChange"
      >
        <el-option label="激活" value="active" />
        <el-option label="禁用" value="inactive" />
      </el-select>
    </div>

    <!-- 用户表格 -->
    <el-table
      :data="users"
      v-loading="loading"
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="role" label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="180" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '激活' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button 
            size="small" 
            :type="row.is_active ? 'warning' : 'success'"
            @click="handleToggleStatus(row)"
          >
            {{ row.is_active ? '禁用' : '激活' }}
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDelete(row)"
            v-if="row.id !== authStore.user?.id"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.current"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="showUserDialog"
      :title="editingUser ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <UserForm
        :user="editingUser"
        @success="handleUserFormSuccess"
        @cancel="showUserDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { userService } from '@/services/userService'
import UserForm from '@/components/UserForm.vue'

const authStore = useAuthStore()

const users = ref([])
const loading = ref(false)
const showUserDialog = ref(false)
const editingUser = ref(null)

const filters = reactive({
  search: '',
  role: '',
  status: ''
})

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 加载用户数据
const loadUsers = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.current,
      per_page: pagination.size,
      search: filters.search || undefined,
      role: filters.role || undefined,
      status: filters.status || undefined
    }

    const response = await userService.getUsers(params)
    users.value = response.users
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载用户失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadUsers()
}

const handleFilterChange = () => {
  pagination.current = 1
  loadUsers()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.current = 1
  loadUsers()
}

const handleCurrentChange = (page) => {
  pagination.current = page
  loadUsers()
}

const handleEdit = (user) => {
  editingUser.value = user
  showUserDialog.value = true
}

const handleToggleStatus = async (user) => {
  try {
    const action = user.is_active ? '禁用' : '激活'
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.username}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await userService.updateUser(user.id, {
      is_active: !user.is_active
    })

    ElMessage.success(`用户${action}成功`)
    loadUsers()
  } catch (error) {
    // 用户取消操作
  }
}

const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )

    await userService.deleteUser(user.id)
    ElMessage.success('用户删除成功')
    loadUsers()
  } catch (error) {
    // 用户取消删除
  }
}

const handleUserFormSuccess = () => {
  showUserDialog.value = false
  editingUser.value = null
  loadUsers()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  width: 300px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
}
</style>