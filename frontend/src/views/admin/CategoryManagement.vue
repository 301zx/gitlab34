<template>
  <div class="category-management">
    <div class="page-header">
      <h2>分类管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索分类..."
          style="width: 300px; margin-right: 10px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </template>
        </el-input>
        <el-button type="primary" @click="dialogVisible = true">
          <el-icon><Plus /></el-icon>
          添加分类
        </el-button>
      </div>
    </div>

    <el-card shadow="hover" class="category-table-card">
      <el-table
        v-loading="loading"
        :data="categories"
        style="width: 100%"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" min-width="150" />
        <el-table-column prop="description" label="分类描述" min-width="200" />
        <el-table-column prop="parent_id" label="父分类ID" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
              style="margin-right: 5px"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row.id)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="categoryForm.description"
            placeholder="请输入分类描述"
            type="textarea"
            rows="3"
          />
        </el-form-item>
        <el-form-item label="父分类ID" prop="parent_id">
          <el-input
            v-model.number="categoryForm.parent_id"
            placeholder="请输入父分类ID（可选）"
            type="number"
          />
          <div class="form-hint">留空表示顶级分类</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { categoriesService } from '@/services/categoriesService'
import {
  Search,
  Plus,
  Edit,
  Delete
} from '@element-plus/icons-vue'

// 搜索和筛选
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const categories = ref([])

// 表单相关
const dialogVisible = ref(false)
const categoryFormRef = ref(null)
const editingCategoryId = ref(null)
const categoryForm = reactive({
  name: '',
  description: '',
  parent_id: null
})

const formRules = reactive({
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 100, message: '分类名称长度在1-100个字符之间', trigger: 'blur' }
  ]
})

const dialogTitle = computed(() => {
  return editingCategoryId.value ? '编辑分类' : '添加分类'
})

// 初始化数据
onMounted(() => {
  fetchCategories()
})

// 获取分类列表
const fetchCategories = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    const response = await categoriesService.getCategories(params)
    categories.value = response.categories || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('获取分类列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 搜索分类
const handleSearch = () => {
  currentPage.value = 1
  fetchCategories()
}

// 分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchCategories()
}

// 当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchCategories()
}

// 打开添加对话框
const openAddDialog = () => {
  editingCategoryId.value = null
  resetForm()
  dialogVisible.value = true
}

// 打开编辑对话框
const handleEdit = (category) => {
  editingCategoryId.value = category.id
  // 填充表单数据
  Object.assign(categoryForm, category)
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  if (categoryFormRef.value) {
    categoryFormRef.value.resetFields()
  }
  Object.assign(categoryForm, {
    name: '',
    description: '',
    parent_id: null
  })
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
  editingCategoryId.value = null
}

// 提交表单
const handleSubmit = async () => {
  if (!categoryFormRef.value) return
  
  try {
    await categoryFormRef.value.validate()
    
    let response
    if (editingCategoryId.value) {
      // 编辑分类
      response = await categoriesService.updateCategory(editingCategoryId.value, categoryForm)
      ElMessage.success('分类更新成功')
    } else {
      // 添加分类
      response = await categoriesService.createCategory(categoryForm)
      ElMessage.success('分类添加成功')
    }
    
    dialogVisible.value = false
    handleDialogClose()
    fetchCategories()
  } catch (error) {
    if (error.name === 'Error') {
      ElMessage.error('操作失败: ' + error.message)
    }
    // 表单验证失败会自动处理
  }
}

// 删除分类
const handleDelete = async (categoryId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个分类吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await categoriesService.deleteCategory(categoryId)
    ElMessage.success('分类删除成功')
    fetchCategories()
  } catch (error) {
    // 错误提示已在响应拦截器中处理，这里只需要处理用户取消操作的情况
    if (error === 'cancel') {
      // 用户取消操作，不显示任何提示
    }
  }
}

// 选择变化
const handleSelectionChange = (selection) => {
  // 可以在这里处理多选操作
}
</script>

<style scoped>
.category-management {
  padding: 20px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
}

.category-table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  text-align: right;
}

.form-hint {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}
</style>
