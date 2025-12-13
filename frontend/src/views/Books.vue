<template>
  <div class="books-container">
    <div class="books-header">
      <h2>图书浏览</h2>
      <el-button 
        type="primary" 
        v-if="authStore.isAdmin"
        @click="showAddBookDialog = true"
      >
        <el-icon><Plus /></el-icon>
        添加图书
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="books-filter">
      <el-input
        v-model="filters.search"
        placeholder="搜索书名、作者或ISBN"
        class="filter-input"
        @input="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>

      <el-select
        v-model="filters.category"
        placeholder="选择分类"
        clearable
        @change="handleFilterChange"
      >
        <el-option
          v-for="category in categories"
          :key="category.id"
          :label="category.name"
          :value="category.id"
        />
      </el-select>

      <el-button @click="resetFilters">重置筛选</el-button>
    </div>

    <!-- 图书列表 -->
    <div class="books-list">
      <el-row :gutter="20">
        <el-col 
          v-for="book in books" 
          :key="book.id"
          :xs="24" :sm="12" :md="8" :lg="6"
        >
          <el-card class="book-card" shadow="hover">
            <template #header>
              <div class="book-header">
                <h3 class="book-title">{{ book.title }}</h3>
                <el-tag 
                  :type="book.available_copies > 0 ? 'success' : 'danger'"
                  size="small"
                >
                  {{ book.available_copies > 0 ? '可借阅' : '已借完' }}
                </el-tag>
              </div>
            </template>

            <div class="book-info">
              <p><strong>作者:</strong> {{ book.author }}</p>
              <p><strong>出版社:</strong> {{ book.publisher || '未知' }}</p>
              <p><strong>ISBN:</strong> {{ book.isbn }}</p>
              <p><strong>库存:</strong> {{ book.available_copies }}/{{ book.total_copies }}</p>
            </div>

            <template #footer>
              <div class="book-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  :disabled="book.available_copies === 0"
                  @click="handleBorrow(book)"
                >
                  借阅
                </el-button>
                <el-button 
                  size="small"
                  @click="viewBookDetail(book)"
                >
                  详情
                </el-button>
                <el-button 
                  v-if="authStore.isAdmin"
                  type="danger" 
                  size="small"
                  @click="handleEdit(book)"
                >
                  编辑
                </el-button>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[12, 24, 36, 48]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 添加/编辑图书对话框 -->
    <el-dialog
      v-model="showAddBookDialog"
      :title="editingBook ? '编辑图书' : '添加图书'"
      width="600px"
    >
      <BookForm
        :book="editingBook"
        @success="handleBookFormSuccess"
        @cancel="showAddBookDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { bookService } from '@/services/bookService'
import BookForm from '@/components/BookForm.vue'

const authStore = useAuthStore()

const books = ref([])
const categories = ref([])
const showAddBookDialog = ref(false)
const editingBook = ref(null)

const filters = reactive({
  search: '',
  category: null
})

const pagination = reactive({
  current: 1,
  size: 12,
  total: 0
})

// 加载图书数据
const loadBooks = async () => {
  try {
    const params = {
      page: pagination.current,
      per_page: pagination.size,
      search: filters.search || undefined,
      category_id: filters.category || undefined
    }

    const response = await bookService.getBooks(params)
    books.value = response.books
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载图书失败')
    console.error(error)
  }
}

// 加载分类数据
const loadCategories = async () => {
  try {
    // 这里需要实现分类服务
    // categories.value = await categoryService.getCategories()
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadBooks()
}

const handleFilterChange = () => {
  pagination.current = 1
  loadBooks()
}

const resetFilters = () => {
  filters.search = ''
  filters.category = null
  pagination.current = 1
  loadBooks()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.current = 1
  loadBooks()
}

const handleCurrentChange = (page) => {
  pagination.current = page
  loadBooks()
}

const handleBorrow = async (book) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要借阅《${book.title}》吗？`,
      '确认借阅',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 调用借阅服务
    // await borrowService.borrowBook(book.id)
    ElMessage.success('借阅成功！')
    loadBooks() // 刷新列表
  } catch (error) {
    // 用户取消
  }
}

const viewBookDetail = (book) => {
  // 跳转到图书详情页
  // router.push(`/books/${book.id}`)
  ElMessage.info(`查看图书详情: ${book.title}`)
}

const handleEdit = (book) => {
  editingBook.value = book
  showAddBookDialog.value = true
}

const handleBookFormSuccess = () => {
  showAddBookDialog.value = false
  editingBook.value = null
  loadBooks()
}

onMounted(() => {
  loadBooks()
  loadCategories()
})
</script>

<style scoped>
.books-container {
  padding: 20px;
}

.books-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.books-filter {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.books-container {
  padding: 20px;
}

.books-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.books-filter {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-input {
  width: 300px;
}

.books-list {
  min-height: 400px;
}

.book-card {
  margin-bottom: 20px;
  height: 100%;
  transition: transform 0.3s;
}

.book-card:hover {
  transform: translateY(-5px);
}

.book-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.book-title {
  margin: 0;
  font-size: 16px;
  line-height: 1.4;
  flex: 1;
  margin-right: 10px;
}

.book-info {
  font-size: 14px;
  line-height: 1.6;
}

.book-info p {
  margin-bottom: 8px;
}

.book-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

@media (max-width: 768px) {
  .books-filter {
    flex-direction: column;
  }
  
  .filter-input {
    width: 100%;
  }
  
  .books-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .book-actions {
    flex-direction: column;
  }
}
</style>