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

    <!-- 高级搜索 -->
    <div class="advanced-search">
      <el-collapse v-model="activeAdvancedSearch">
        <el-collapse-item title="高级搜索" name="advanced">
          <div class="advanced-search-form">
            <el-input
              v-model="filters.publisher"
              placeholder="按出版社搜索"
              class="advanced-filter-input"
              @input="handleSearch"
            />

            <div class="year-range">
              <span class="year-label">出版年份：</span>
              <el-input-number
                v-model="filters.minPublishYear"
                :min="1900"
                :max="new Date().getFullYear()"
                placeholder="起始年份"
                @change="handleSearch"
              />
              <span class="year-separator">至</span>
              <el-input-number
                v-model="filters.maxPublishYear"
                :min="1900"
                :max="new Date().getFullYear()"
                placeholder="结束年份"
                @change="handleSearch"
              />
            </div>

            <el-checkbox
              v-model="filters.availableOnly"
              @change="handleSearch"
            >
              仅显示可借阅图书
            </el-checkbox>
          </div>
        </el-collapse-item>
      </el-collapse>
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
                  v-if="book.available_copies > 0"
                >
                  借阅
                </el-button>
                <el-button 
                  type="info" 
                  size="small"
                  @click="handleReservation(book)"
                  v-else
                >
                  预约
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { bookService } from '@/services/bookService'
import { categoriesService } from '@/services/categoriesService'
import { borrowService } from '@/services/borrowService'
import { reservationService } from '@/services/reservationService'
import BookForm from '@/components/BookForm.vue'

const authStore = useAuthStore()
const router = useRouter()

const books = ref([])
const categories = ref([])
const showAddBookDialog = ref(false)
const editingBook = ref(null)
const activeAdvancedSearch = ref([])

const filters = reactive({
  search: '',
  category: null,
  publisher: '',
  minPublishYear: null,
  maxPublishYear: null,
  availableOnly: false
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
      category_id: filters.category || undefined,
      publisher: filters.publisher || undefined,
      min_publish_year: filters.minPublishYear || undefined,
      max_publish_year: filters.maxPublishYear || undefined,
      available_only: filters.availableOnly || undefined
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
    // 注意：categoriesService已经实现，直接调用即可
    const response = await categoriesService.getCategories()
    categories.value = response
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
  filters.publisher = ''
  filters.minPublishYear = null
  filters.maxPublishYear = null
  filters.availableOnly = false
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
    await borrowService.borrowBook(book.id)
    ElMessage.success('借阅成功！')
    loadBooks() // 刷新列表
  } catch (error) {
    // 如果是用户取消，不显示错误信息
    if (error !== 'cancel') {
      ElMessage.error(error.message || '借阅失败，请稍后重试')
    }
  }
}

const handleReservation = async (book) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要预约《${book.title}》吗？预约有效期为7天。`,
      '确认预约',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    // 调用预约服务
    await reservationService.createReservation(book.id)
    ElMessage.success('预约成功！')
    loadBooks() // 刷新列表
  } catch (error) {
    // 如果是用户取消，不显示错误信息
    if (error !== 'cancel') {
      ElMessage.error(error.message || '预约失败，请稍后重试')
    }
  }
}

const viewBookDetail = (book) => {
  // 跳转到图书详情页
  router.push(`/books/${book.id}`)
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

/* 高级搜索样式 */
.advanced-search {
  margin: 15px 0 20px;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 8px;
}

.advanced-search-form {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
  padding: 15px 0;
}

.advanced-filter-input {
  width: 200px;
}

.year-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.year-label {
  font-weight: 500;
  color: #606266;
}

.year-separator {
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .books-filter {
    flex-direction: column;
  }
  
  .filter-input,
  .advanced-filter-input {
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
  
  .advanced-search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .year-range {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>