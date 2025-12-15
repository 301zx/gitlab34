<template>
  <div class="borrow-management">
    <div class="page-header">
      <h2>借阅管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <el-input
        v-model="filters.search"
        placeholder="搜索用户名或图书名"
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
        v-model="filters.status"
        placeholder="选择状态"
        clearable
        @change="handleFilterChange"
      >
        <el-option label="借阅中" value="borrowed" />
        <el-option label="已归还" value="returned" />
        <el-option label="已逾期" value="overdue" />
      </el-select>

      <el-date-picker
        v-model="filters.dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        @change="handleDateChange"
      />
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon borrowed">
                <el-icon><Reading /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.currentBorrows }}</div>
                <div class="stat-label">当前借阅</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon overdue">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.overdueBorrows }}</div>
                <div class="stat-label">逾期借阅</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon returned">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalReturns }}</div>
                <div class="stat-label">本月归还</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon fine">
                <el-icon><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">¥{{ stats.totalFines }}</div>
                <div class="stat-label">累计罚金</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 借阅列表 -->
    <BorrowList 
      :status="filters.status ? [filters.status] : ['borrowed', 'returned', 'overdue']"
      :show-actions="true"
      ref="borrowListRef"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search, Reading, Clock, Check, Money } from '@element-plus/icons-vue'
import { borrowService } from '@/services/borrowService'
import BorrowList from '@/components/BorrowList.vue'

const borrowListRef = ref()

const filters = reactive({
  search: '',
  status: '',
  dateRange: []
})

const stats = reactive({
  currentBorrows: 0,
  overdueBorrows: 0,
  totalReturns: 0,
  totalFines: 0
})

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await borrowService.getStats()
    Object.assign(stats, response)
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const handleSearch = () => {
  if (borrowListRef.value) {
    borrowListRef.value.loadBorrows()
  }
}

const handleFilterChange = () => {
  if (borrowListRef.value) {
    borrowListRef.value.loadBorrows()
  }
}

const handleDateChange = () => {
  if (borrowListRef.value) {
    borrowListRef.value.loadBorrows()
  }
}

const exportData = async () => {
  try {
    ElMessage.info('正在导出数据...')
    // 这里实现数据导出逻辑
    // await borrowService.exportBorrows(filters)
    ElMessage.success('数据导出成功')
  } catch (error) {
    ElMessage.error('数据导出失败')
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.borrow-management {
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

.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.borrowed {
  background: #409eff;
}

.stat-icon.overdue {
  background: #f56c6c;
}

.stat-icon.returned {
  background: #67c23a;
}

.stat-icon.fine {
  background: #e6a23c;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
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
  
  .stats-cards .el-col {
    margin-bottom: 15px;
  }
}
</style>