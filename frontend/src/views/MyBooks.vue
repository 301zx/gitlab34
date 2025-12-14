<template>
  <div class="my-books">
    <div class="page-header">
      <h2>我的借阅</h2>
    </div>

    <!-- 筛选标签页 -->
    <el-tabs v-model:active-name="activeTab" class="filter-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="当前借阅" name="current"></el-tab-pane>
      <el-tab-pane label="历史借阅" name="history"></el-tab-pane>
    </el-tabs>

    <el-card shadow="hover" class="borrow-table-card">
      <el-table
        v-loading="loading"
        :data="borrows"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="id" label="借阅ID" width="100" />
        <el-table-column prop="book_id" label="图书ID" width="100" />
        <el-table-column label="图书信息" min-width="300">
          <template #default="scope">
            <div class="book-info">
              <div class="book-title">{{ scope.row.book?.title || '未知图书' }}</div>
              <div class="book-meta">
                <span class="author">{{ scope.row.book?.author || '未知作者' }}</span>
                <span class="isbn">ISBN: {{ scope.row.book?.isbn || '未知ISBN' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="borrow_date" label="借阅日期" width="180" />
        <el-table-column prop="due_date" label="应还日期" width="180" />
        <el-table-column prop="return_date" label="实际归还日期" width="180" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag
              :type="getStatusTagType(scope.row.status)"
              effect="light"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fine_amount" label="罚金" width="100">
          <template #default="scope">
            <span v-if="scope.row.fine_amount > 0" class="fine-amount">
              ¥{{ scope.row.fine_amount.toFixed(2) }}
            </span>
            <span v-else>¥0.00</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <template v-if="scope.row.status === 'borrowed'">
              <el-button
                type="primary"
                size="small"
                @click="handleRenew(scope.row)"
                style="margin-right: 5px"
                :disabled="scope.row.renewed"
              >
                <el-icon><RefreshLeft /></el-icon>
                {{ scope.row.renewed ? '已续借' : '续借' }}
              </el-button>
              <el-button
                type="success"
                size="small"
                @click="handleReturn(scope.row.id)"
              >
                <el-icon><ArrowRight /></el-icon>
                归还
              </el-button>
            </template>
            <template v-else>
              <el-button
                type="info"
                size="small"
                disabled
              >
                已完成
              </el-button>
            </template>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { borrowService } from '@/services/borrowService'
import { bookService } from '@/services/bookService'
import {
  RefreshLeft,
  ArrowRight
} from '@element-plus/icons-vue'

// 状态管理
const activeTab = ref('current')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const borrows = ref([])

// 根据标签页获取筛选状态
const getFilterStatus = () => {
  if (activeTab.value === 'current') {
    return 'borrowed'
  } else {
    return 'returned'
  }
}

// 初始化数据
onMounted(() => {
  fetchBorrows()
})

// 获取借阅记录
const fetchBorrows = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      status: getFilterStatus()
    }
    
    const response = await borrowService.getMyBorrows(params)
    
    // 检查 response 是否存在且包含 borrows 属性
    if (response && response.borrows) {
      borrows.value = response.borrows
      total.value = response.total || 0
      
      // 获取图书详情
      await fetchBookDetails()
    } else {
      // 当 response 不存在或格式不正确时，显示空列表
      borrows.value = []
      total.value = 0
      console.warn('获取借阅记录格式不正确或为空')
    }
  } catch (error) {
    // 处理 API 错误，确保组件不会崩溃
    borrows.value = []
    total.value = 0
    
    // 显示友好的错误提示
    ElMessage.error('获取借阅记录失败')
    console.error('获取借阅记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取图书详情
const fetchBookDetails = async () => {
  for (const borrow of borrows.value) {
    try {
      // api.js 响应拦截器已经返回 response.data，所以不需要再访问 .data
      const bookResponse = await bookService.getBook(borrow.book_id)
      borrow.book = bookResponse
    } catch (error) {
      console.error(`获取图书 ${borrow.book_id} 详情失败:`, error)
      borrow.book = null
    }
  }
}

// 标签页切换
const handleTabChange = () => {
  currentPage.value = 1
  fetchBorrows()
}

// 分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchBorrows()
}

// 当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchBorrows()
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'borrowed': '已借阅',
    'returned': '已归还',
    'overdue': '已逾期'
  }
  return statusMap[status] || status
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    'borrowed': 'primary',
    'returned': 'success',
    'overdue': 'danger'
  }
  return typeMap[status] || 'info'
}

// 归还图书
const handleReturn = async (recordId) => {
  try {
    await ElMessageBox.confirm('确定要归还这本图书吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await borrowService.returnBook(recordId)
    ElMessage.success('图书归还成功')
    fetchBorrows()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('归还失败: ' + error.message)
    }
  }
}

// 续借图书
const handleRenew = async (borrowRecord) => {
  try {
    await ElMessageBox.confirm('确定要续借这本图书吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await borrowService.renewBook(borrowRecord.id)
    ElMessage.success('图书续借成功')
    fetchBorrows()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('续借失败: ' + error.message)
    }
  }
}
</script>

<style scoped>
.my-books {
  padding: 20px 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.filter-tabs {
  margin-bottom: 20px;
}

.borrow-table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.book-info {
  display: flex;
  flex-direction: column;
}

.book-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.book-meta {
  display: flex;
  flex-direction: column;
  font-size: 12px;
  color: #606266;
}

.author {
  margin-bottom: 2px;
}

.fine-amount {
  color: #f56c6c;
  font-weight: 500;
}
</style>
