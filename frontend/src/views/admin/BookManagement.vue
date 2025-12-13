<template>
  <div class="book-management">
    <div class="page-header">
      <h2>图书管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索图书..."
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
          添加图书
        </el-button>
      </div>
    </div>

    <el-card shadow="hover" class="book-table-card">
      <el-table
        v-loading="loading"
        :data="books"
        style="width: 100%"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="isbn" label="ISBN" width="150" />
        <el-table-column prop="title" label="书名" min-width="200" />
        <el-table-column prop="author" label="作者" width="150" />
        <el-table-column prop="publisher" label="出版社" width="180" />
        <el-table-column prop="category_id" label="分类ID" width="100" />
        <el-table-column prop="total_copies" label="总册数" width="100" />
        <el-table-column prop="available_copies" label="可借册数" width="100" />
        <el-table-column prop="created_at" label="添加时间" width="180" formatter="dateFormatter" />
        <el-table-column label="操作" width="200" fixed="right">
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

    <!-- 添加/编辑图书对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="bookFormRef"
        :model="bookForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="bookForm.isbn" placeholder="请输入ISBN" />
        </el-form-item>
        <el-form-item label="书名" prop="title">
          <el-input v-model="bookForm.title" placeholder="请输入书名" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="bookForm.author" placeholder="请输入作者" />
        </el-form-item>
        <el-form-item label="出版社" prop="publisher">
          <el-input v-model="bookForm.publisher" placeholder="请输入出版社" />
        </el-form-item>
        <el-form-item label="出版日期" prop="publish_date">
          <el-date-picker
            v-model="bookForm.publish_date"
            type="date"
            placeholder="选择出版日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="分类ID" prop="category_id">
          <el-input
            v-model.number="bookForm.category_id"
            placeholder="请输入分类ID"
            type="number"
          />
        </el-form-item>
        <el-form-item label="总册数" prop="total_copies">
          <el-input
            v-model.number="bookForm.total_copies"
            placeholder="请输入总册数"
            type="number"
            min="1"
          />
        </el-form-item>
        <el-form-item label="可借册数" prop="available_copies">
          <el-input
            v-model.number="bookForm.available_copies"
            placeholder="请输入可借册数"
            type="number"
            min="0"
          />
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
import { bookService } from '@/services/bookService'
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
const books = ref([])
const categories = ref([])

// 表单相关
const dialogVisible = ref(false)
const bookFormRef = ref(null)
const editingBookId = ref(null)
const bookForm = reactive({
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  publish_date: null,
  category_id: null,
  total_copies: 1,
  available_copies: 1
})

const formRules = reactive({
  isbn: [
    { required: true, message: '请输入ISBN', trigger: 'blur' },
    { min: 10, max: 20, message: 'ISBN长度在10-20个字符之间', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入书名', trigger: 'blur' },
    { min: 1, max: 255, message: '书名长度在1-255个字符之间', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者', trigger: 'blur' },
    { min: 1, max: 255, message: '作者长度在1-255个字符之间', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请输入分类ID', trigger: 'blur' },
    { type: 'number', message: '分类ID必须是数字', trigger: 'blur' }
  ],
  total_copies: [
    { required: true, message: '请输入总册数', trigger: 'blur' },
    { type: 'number', min: 1, message: '总册数必须大于0', trigger: 'blur' }
  ],
  available_copies: [
    { required: true, message: '请输入可借册数', trigger: 'blur' },
    { type: 'number', min: 0, message: '可借册数必须大于等于0', trigger: 'blur' }
  ]
})

const dialogTitle = computed(() => {
  return editingBookId.value ? '编辑图书' : '添加图书'
})

// 初始化数据
onMounted(() => {
  fetchBooks()
  fetchCategories()
})

// 获取图书列表
const fetchBooks = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    const response = await bookService.getBooks(params)
    books.value = response.data.books
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取图书列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await categoriesService.getCategories()
    categories.value = response.data
  } catch (error) {
    ElMessage.error('获取分类列表失败: ' + error.message)
  }
}

// 搜索图书
const handleSearch = () => {
  currentPage.value = 1
  fetchBooks()
}

// 分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchBooks()
}

// 当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchBooks()
}

// 打开添加对话框
const openAddDialog = () => {
  editingBookId.value = null
  resetForm()
  dialogVisible.value = true
}

// 打开编辑对话框
const handleEdit = (book) => {
  editingBookId.value = book.id
  // 填充表单数据
  Object.assign(bookForm, {
    ...book,
    publish_date: book.publish_date ? new Date(book.publish_date) : null
  })
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  if (bookFormRef.value) {
    bookFormRef.value.resetFields()
  }
  Object.assign(bookForm, {
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    publish_date: null,
    category_id: null,
    total_copies: 1,
    available_copies: 1
  })
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
  editingBookId.value = null
}

// 提交表单
const handleSubmit = async () => {
  if (!bookFormRef.value) return
  
  try {
    await bookFormRef.value.validate()
    
    const formData = {
      ...bookForm,
      publish_date: bookForm.publish_date ? bookForm.publish_date.toISOString().split('T')[0] : null
    }
    
    let response
    if (editingBookId.value) {
      // 编辑图书
      response = await bookService.updateBook(editingBookId.value, formData)
      ElMessage.success('图书更新成功')
    } else {
      // 添加图书
      response = await bookService.createBook(formData)
      ElMessage.success('图书添加成功')
    }
    
    dialogVisible.value = false
    handleDialogClose()
    fetchBooks()
  } catch (error) {
    if (error.name === 'Error') {
      ElMessage.error('操作失败: ' + error.message)
    }
    // 表单验证失败会自动处理
  }
}

// 删除图书
const handleDelete = async (bookId) => {
  try {
    await ElMessageBox.confirm('确定要删除这本图书吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await bookService.deleteBook(bookId)
    ElMessage.success('图书删除成功')
    fetchBooks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 选择变化
const handleSelectionChange = (selection) => {
  // 可以在这里处理多选操作
}
</script>

<style scoped>
.book-management {
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

.book-table-card {
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
</style>
