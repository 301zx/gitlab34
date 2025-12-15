<template>
  <div class="log-management">
    <div class="page-header">
      <h2>系统日志</h2>
      <p>查看和管理系统运行日志</p>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <el-select
        v-model="filters.level"
        placeholder="选择日志级别"
        clearable
        @change="loadLogs"
        class="filter-select"
      >
        <el-option label="INFO" value="INFO" />
        <el-option label="WARNING" value="WARNING" />
        <el-option label="ERROR" value="ERROR" />
        <el-option label="DEBUG" value="DEBUG" />
      </el-select>

      <el-button type="primary" @click="loadLogs">
        <el-icon><Search /></el-icon>
        查询
      </el-button>

      <el-button @click="clearLogs">
        <el-icon><Delete /></el-icon>
        清空日志
      </el-button>
    </div>

    <!-- 日志列表 -->
    <el-card class="log-card">
      <div class="log-list" v-if="logs.length > 0">
        <div
          v-for="(log, index) in logs"
          :key="index"
          class="log-item"
          :class="getLogClass(log)"
        >
          <div class="log-time">{{ getLogTime(log) }}</div>
          <div class="log-content">{{ log }}</div>
        </div>
      </div>
      <div v-else class="empty-state">
        <el-empty description="暂无日志" />
      </div>
    </el-card>

    <!-- 分页 -->
    <div class="pagination" v-if="pagination.total > pagination.per_page">
      <el-pagination
        v-model:current-page="pagination.current"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Delete } from '@element-plus/icons-vue'
import { logService } from '@/services/logService'

const logs = ref([])
const loading = ref(false)

const filters = reactive({
  level: ''
})

const pagination = reactive({
  current: 1,
  per_page: 20,
  total: 0
})

// 加载日志
const loadLogs = async () => {
  loading.value = true
  try {
    const response = await logService.getLogs({
      page: pagination.current,
      per_page: pagination.per_page,
      level: filters.level
    })
    
    logs.value = response.logs
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载日志失败')
    console.error('加载日志失败:', error)
  } finally {
    loading.value = false
  }
}

// 清空日志
const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await logService.clearLogs()
    ElMessage.success('日志已清空')
    loadLogs()
  } catch (error) {
    // 用户取消操作
  }
}

// 根据日志内容获取日志级别样式
const getLogClass = (log) => {
  if (log.includes('ERROR')) return 'log-error'
  if (log.includes('WARNING')) return 'log-warning'
  if (log.includes('DEBUG')) return 'log-debug'
  return 'log-info'
}

// 从日志中提取时间
const getLogTime = (log) => {
  const timeMatch = log.match(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/)
  return timeMatch ? timeMatch[0] : ''
}

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.current = 1
  loadLogs()
}

// 当前页码变化
const handleCurrentChange = (page) => {
  pagination.current = page
  loadLogs()
}

// 初始化
onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.log-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-select {
  width: 150px;
}

.log-card {
  max-height: 600px;
  overflow: hidden;
}

.log-list {
  max-height: 550px;
  overflow-y: auto;
  padding: 10px 0;
}

.log-item {
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  display: flex;
}

.log-time {
  width: 180px;
  color: #909399;
  margin-right: 16px;
  font-weight: 500;
}

.log-content {
  flex: 1;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-info {
  background-color: #f0f9ff;
}

.log-warning {
  background-color: #fdf6ec;
}

.log-error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.log-debug {
  background-color: #f0f0f0;
}

.empty-state {
  padding: 40px 0;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .log-item {
    flex-direction: column;
  }
  
  .log-time {
    width: auto;
    margin-right: 0;
    margin-bottom: 4px;
  }
}
</style>
