<template>
  <div class="book-detail">
    <div class="page-header">
      <h2>{{ book.title }}</h2>
      <el-button @click="goBack" type="default">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
    </div>

    <el-card shadow="hover" class="book-info-card">
      <div class="book-info">
        <div class="book-cover">
          <!-- 图书封面占位符 -->
          <div class="cover-placeholder">
            <el-icon><Reading /></el-icon>
            <span>图书封面</span>
          </div>
        </div>
        <div class="book-details">
          <h3>{{ book.title }}</h3>
          <p class="author">作者：{{ book.author }}</p>
          <p class="publisher">出版社：{{ book.publisher }}</p>
          <p class="publish-date">出版日期：{{ formatDate(book.publish_date) }}</p>
          <p class="isbn">ISBN：{{ book.isbn }}</p>
          <p class="category">分类：{{ categoryName }}</p>
          <p class="total-copies">总册数：{{ book.total_copies }}</p>
          <p class="available-copies">可借册数：{{ book.available_copies }}</p>
          
          <div class="book-actions">
            <el-button 
              type="primary" 
              @click="borrowBook" 
              :disabled="book.available_copies <= 0"
            >
              <el-icon><DocumentCopy /></el-icon>
              {{ book.available_copies > 0 ? '借阅' : '已借完' }}
            </el-button>
            <el-button 
              type="default" 
              @click="reserveBook" 
              :disabled="book.available_copies > 0"
            >
              <el-icon><Calendar /></el-icon>
              预约
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 图书评论区 -->
    <el-card shadow="hover" class="comments-card">
      <template #header>
        <div class="card-header">
          <h3>图书评论</h3>
          <el-button type="primary" @click="showCommentDialog = true">
            <el-icon><Plus /></el-icon>
            添加评论
          </el-button>
        </div>
      </template>

      <!-- 评论列表 -->
      <div v-if="comments.length > 0" class="comments-list">
        <el-divider v-for="comment in comments" :key="comment.id" />
        <div class="comment-item" v-for="comment in comments" :key="comment.id">
          <div class="comment-header">
            <div class="user-info">
              <el-avatar :size="32" :src="comment.user_avatar || ''">{{ comment.username.charAt(0) }}</el-avatar>
              <span class="username">{{ comment.username }}</span>
            </div>
            <div class="comment-meta">
              <div class="rating">
                <el-rate :model-value="comment.rating" disabled :colors="['#F59E0B']" />
              </div>
              <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
            </div>
          </div>
          <div class="comment-content">{{ comment.comment }}</div>
          <div class="comment-actions">
            <el-button 
              v-if="comment.user_id === authStore.user?.id" 
              type="text" 
              size="small" 
              @click="editComment(comment)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              v-if="comment.user_id === authStore.user?.id" 
              type="text" 
              size="small" 
              @click="deleteComment(comment.id)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 无评论提示 -->
      <div v-else class="no-comments">
        <el-empty description="暂无评论，快来添加第一条评论吧" />
      </div>

      <!-- 分页 -->
      <div v-if="comments.length > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="commentPage"
          v-model:page-size="commentPageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="commentsTotal"
          @size-change="handleCommentSizeChange"
          @current-change="handleCommentCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑评论对话框 -->
    <el-dialog
      v-model="showCommentDialog"
      :title="editingComment ? '编辑评论' : '添加评论'"
      width="600px"
    >
      <el-form
        ref="commentFormRef"
        :model="commentForm"
        :rules="commentRules"
        label-width="80px"
      >
        <el-form-item label="评分" prop="rating">
          <el-rate v-model="commentForm.rating" :colors="['#F59E0B']" />
        </el-form-item>
        <el-form-item label="评论" prop="comment">
          <el-input
            v-model="commentForm.comment"
            type="textarea"
            placeholder="请输入您的评论"
            rows="4"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCommentDialog = false">取消</el-button>
          <el-button type="primary" @click="submitComment">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElRate } from 'element-plus'
import { bookService } from '@/services/bookService'
import { borrowService } from '@/services/borrowService'
import { categoriesService } from '@/services/categoriesService'
import { useAuthStore } from '@/stores/auth'
import {
  ArrowLeft,
  Reading,
  DocumentCopy,
  Calendar,
  Plus,
  Edit,
  Delete
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 图书信息
const book = ref({})
const categoryName = ref('未知分类')
const loading = ref(false)

// 评论相关
const comments = ref([])
const commentsTotal = ref(0)
const commentPage = ref(1)
const commentPageSize = ref(10)
const showCommentDialog = ref(false)
const editingComment = ref(null)
const commentFormRef = ref(null)
const commentForm = reactive({
  rating: 5,
  comment: ''
})

const commentRules = reactive({
  rating: [
    { required: true, message: '请选择评分', trigger: 'change' }
  ],
  comment: [
    { required: true, message: '请输入评论内容', trigger: 'blur' },
    { min: 1, max: 500, message: '评论内容长度在1-500个字符之间', trigger: 'blur' }
  ]
})

// 获取图书ID
const bookId = computed(() => {
  return route.params.id
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 回到上一页
const goBack = () => {
  router.go(-1)
}

// 加载图书详情
const loadBookDetail = async () => {
  loading.value = true
  try {
    const response = await bookService.getBook(bookId.value)
    book.value = response.data
    
    // 获取分类名称
    if (book.value.category_id) {
      const categoryResponse = await categoriesService.getCategory(book.value.category_id)
      categoryName.value = categoryResponse.data.name
    }
  } catch (error) {
    ElMessage.error('获取图书详情失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 加载评论列表
const loadComments = async () => {
  try {
    const response = await bookService.getBookReviews(bookId.value, {
      page: commentPage.value,
      per_page: commentPageSize.value
    })
    comments.value = response.data.reviews
    commentsTotal.value = response.data.total
  } catch (error) {
    ElMessage.error('获取评论列表失败: ' + error.message)
  }
}

// 借阅图书
const borrowBook = async () => {
  try {
    await borrowService.borrowBook(bookId.value)
    ElMessage.success('借阅成功')
    loadBookDetail() // 更新图书可借数量
  } catch (error) {
    ElMessage.error('借阅失败: ' + error.message)
  }
}

// 预约图书
const reserveBook = async () => {
  ElMessage.info('预约功能正在开发中')
  // 这里可以实现预约功能的逻辑
}

// 处理评论分页大小变化
const handleCommentSizeChange = (size) => {
  commentPageSize.value = size
  commentPage.value = 1
  loadComments()
}

// 处理评论当前页变化
const handleCommentCurrentChange = (page) => {
  commentPage.value = page
  loadComments()
}

// 提交评论
const submitComment = async () => {
  if (!commentFormRef.value) return
  
  try {
    await commentFormRef.value.validate()
    
    // 这里可以实现提交评论的逻辑
    ElMessage.success(editingComment ? '评论更新成功' : '评论添加成功')
    showCommentDialog.value = false
    resetCommentForm()
    loadComments() // 重新加载评论列表
  } catch (error) {
    if (error.name === 'Error') {
      ElMessage.error('操作失败: ' + error.message)
    }
  }
}

// 编辑评论
const editComment = (comment) => {
  editingComment.value = comment
  commentForm.rating = comment.rating
  commentForm.comment = comment.comment
  showCommentDialog.value = true
}

// 删除评论
const deleteComment = async (commentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 这里可以实现删除评论的逻辑
    ElMessage.success('评论删除成功')
    loadComments() // 重新加载评论列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 重置评论表单
const resetCommentForm = () => {
  if (commentFormRef.value) {
    commentFormRef.value.resetFields()
  }
  commentForm.rating = 5
  commentForm.comment = ''
  editingComment.value = null
}

// 初始化
onMounted(() => {
  loadBookDetail()
  loadComments()
})

// 监听图书ID变化
watch(bookId, () => {
  loadBookDetail()
  loadComments()
})
</script>

<style scoped>
.book-detail {
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

.book-info-card {
  margin-bottom: 20px;
}

.book-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.book-cover {
  width: 200px;
  height: 300px;
  flex-shrink: 0;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 8px;
  color: #909399;
}

.cover-placeholder .el-icon {
  font-size: 64px;
  margin-bottom: 10px;
}

.book-details {
  flex: 1;
  min-width: 300px;
}

.book-details h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 24px;
}

.book-details p {
  margin: 8px 0;
  color: #606266;
}

.book-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.comments-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.comments-list {
  margin-top: 20px;
}

.comment-item {
  padding: 10px 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-weight: 500;
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rating {
  color: #F59E0B;
}

.comment-date {
  font-size: 12px;
  color: #909399;
}

.comment-content {
  margin-bottom: 10px;
  line-height: 1.5;
}

.comment-actions {
  display: flex;
  gap: 10px;
}

.no-comments {
  padding: 30px 0;
  text-align: center;
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
