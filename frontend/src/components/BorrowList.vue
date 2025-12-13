<template>
  <div class="borrow-list">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="borrows.length === 0" class="empty-state">
      <el-empty description="暂无借阅记录" />
    </div>

    <div v-else class="borrows-container">
      <el-table :data="borrows" style="width: 100%">
        <el-table-column prop="book.title" label="图书名称" min-width="200">
          <template #default="{ row }">
            <div class="book-info">
              <strong>{{ row.book.title }}</strong>
              <div class="book-meta">
                <span>作者: {{ row.book.author }}</span>
                <span>ISBN: {{ row.book.isbn }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="borrow_date" label="借阅日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.borrow_date) }}
          </template>
        </el-table-column>

        <el-table-column prop="due_date" label="应还日期" width="120">
          <template #default="{ row }">
            <span :class="getDueDateClass(row)">
              {{ formatDate(row.due_date) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="return_date" label="归还日期" width="120">
          <template #default="{ row }">
            {{ row.return_date ? formatDate(row.return_date) : '未归还' }}
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="fine_amount" label="罚金" width="100">
          <template #default="{ row }">
            <span v-if="row.fine_amount > 0" class="fine-amount">
              ¥{{ row.fine_amount }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" v-if="showActions">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'borrowed'" 
              size="small" 
              @click="handleReturn(row)"
            >
              归还
            </el-button>
            <el-button 
              v-if="row.status === 'borrowed' && canRenew(row)" 
              size="small"
              @click="handleRenew(row)"
            >
              续借
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination" v-if="pagination.total > pagination.size">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { borrowService } from '@/services/borrowService'

const props = defineProps({
  status: {
    type: Array,
    default: () => ['borrowed', 'returned', 'overdue']
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

const borrows = ref([])
const loading = ref(false)

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 加载借阅记录
const loadBorrows = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.current,
      per_page: pagination.size,
      status: props.status
    }

    const response = await borrowService.getMyBorrows(params)
    borrows.value = response.borrows
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载借阅记录失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 获取状态样式
const getStatusType = (status) => {
  const types = {
    borrowed: 'primary',
    returned: 'success',
    overdue: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    borrowed: '借阅中',
    returned: '已归还',
    overdue: '已逾期'
  }
  return texts[status] || status
}

// 检查是否逾期
const getDueDateClass = (row) => {
  if (row.status === 'returned') return 'returned'
  if (row.status === 'overdue') return 'overdue'
  
  const dueDate = new Date(row.due_date)
  const today = new Date()
  if (dueDate < today) return 'overdue'
  
  return 'normal'
}

// 检查是否可以续借
const canRenew = (row) => {
  const borrowDate = new Date(row.borrow_date)
  const today = new Date()
  const diffTime = today - borrowDate
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  // 假设借阅超过7天才可以续借
  return diffDays >= 7
}

// 归还图书
const handleReturn = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要归还《${row.book.title}》吗？`,
      '确认归还',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await borrowService.returnBook(row.id)
    ElMessage.success('归还成功')
    loadBorrows() // 刷新列表
  } catch (error) {
    // 用户取消操作
  }
}

// 续借图书
const handleRenew = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要续借《${row.book.title}》吗？续借期限为30天。`,
      '确认续借',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await borrowService.renewBook(row.id)
    ElMessage.success('续借成功')
    loadBorrows() // 刷新列表
  } catch (error) {
    // 用户取消操作
  }
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.current = 1
  loadBorrows()
}

const handleCurrentChange = (page) => {
  pagination.current = page
  loadBorrows()
}

// 监听status变化重新加载数据
watch(() => props.status, () => {
  pagination.current = 1
  loadBorrows()
}, { immediate: true })

onMounted(() => {
  loadBorrows()
})
</script>

<style scoped>
.borrow-list {
  min-height: 400px;
}

.loading-container {
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.book-info strong {
  display: block;
  margin-bottom: 4px;
}

.book-meta {
  font-size: 12px;
  color: #909399;
}

.book-meta span {
  margin-right: 12px;
}

.overdue {
  color: #f56c6c;
  font-weight: bold;
}

.returned {
  color: #67c23a;
}

.fine-amount {
  color: #f56c6c;
  font-weight: bold;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>