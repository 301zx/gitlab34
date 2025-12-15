<template>
  <div class="statistics">
    <div class="page-header">
      <h2>数据统计</h2>
    </div>

    <!-- 总体概览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-title">图书总数</div>
            <div class="card-value">{{ overviewStats.totalBooks }}</div>
            <div class="card-icon book-icon">
              <el-icon><Reading /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-title">用户总数</div>
            <div class="card-value">{{ overviewStats.totalUsers }}</div>
            <div class="card-icon user-icon">
              <el-icon><User /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-title">当前借阅数</div>
            <div class="card-value">{{ overviewStats.currentBorrows }}</div>
            <div class="card-icon borrow-icon">
              <el-icon><DocumentCopy /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-title">逾期数</div>
            <div class="card-value">{{ overviewStats.overdueCount }}</div>
            <div class="card-icon overdue-icon">
              <el-icon><WarningFilled /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>借阅趋势</span>
              <el-select v-model="dateRange" placeholder="选择时间范围" size="small">
                <el-option label="最近7天" value="7d"></el-option>
                <el-option label="最近30天" value="30d"></el-option>
                <el-option label="最近90天" value="90d"></el-option>
              </el-select>
            </div>
          </template>
          <div ref="trendChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>借阅状态分布</span>
            </div>
          </template>
          <div ref="statusChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>热门图书</span>
            </div>
          </template>
          <div class="top-books">
            <el-table
              v-loading="loading"
              :data="topBooks"
              style="width: 100%"
              stripe
            >
              <el-table-column label="排名" width="80" type="index" :index="index => index + 1"></el-table-column>
              <el-table-column prop="title" label="书名" min-width="200"></el-table-column>
              <el-table-column prop="author" label="作者" width="150"></el-table-column>
              <el-table-column prop="borrow_count" label="借阅次数" width="120"></el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>用户借阅排名</span>
            </div>
          </template>
          <div class="top-users">
            <el-table
              v-loading="loading"
              :data="topUsers"
              style="width: 100%"
              stripe
            >
              <el-table-column label="排名" width="80" type="index" :index="index => index + 1"></el-table-column>
              <el-table-column prop="username" label="用户名" width="120"></el-table-column>
              <el-table-column prop="email" label="邮箱" width="200"></el-table-column>
              <el-table-column prop="borrow_count" label="借阅次数" width="120"></el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { borrowService } from '@/services/borrowService'
import {
  Reading,
  User,
  DocumentCopy,
  WarningFilled
} from '@element-plus/icons-vue'

// 状态管理
const loading = ref(false)
const dateRange = ref('7d')
const overviewStats = reactive({
  totalBooks: 0,
  totalUsers: 0,
  currentBorrows: 0,
  overdueCount: 0
})

// 图表引用
const trendChart = ref(null)
const statusChart = ref(null)

// 数据
const topBooks = ref([])
const topUsers = ref([])
const borrowTrend = ref([])
const statusDistribution = ref([])

// 初始化数据
onMounted(() => {
  fetchStatistics()
})

// 监听日期范围变化
watch(dateRange, () => {
  fetchStatistics()
})

// 获取统计数据
const fetchStatistics = async () => {
  loading.value = true
  try {
    // 获取借阅统计数据
    const statsResponse = await borrowService.getBorrowStats({ range: dateRange.value })
    
    // 更新概览数据
    overviewStats.totalBooks = statsResponse.overview.totalBooks || 0
    overviewStats.totalUsers = statsResponse.overview.totalUsers || 0
    overviewStats.currentBorrows = statsResponse.overview.currentBorrows || 0
    overviewStats.overdueCount = statsResponse.overview.overdueCount || 0
    
    // 更新热门图书
    topBooks.value = statsResponse.topBooks || []
    
    // 更新用户借阅排名
    topUsers.value = statsResponse.topUsers || []
    
    // 更新借阅趋势
    borrowTrend.value = statsResponse.borrowTrend || []
    
    // 更新借阅状态分布
    statusDistribution.value = statsResponse.statusDistribution || []
    
    // 渲染图表
    nextTick(() => {
      renderTrendChart()
      renderStatusChart()
    })
  } catch (error) {
    ElMessage.error('获取统计数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 渲染借阅趋势图表
const renderTrendChart = () => {
  if (!trendChart.value) return
  
  // 动态导入 ECharts
  import('echarts').then(echarts => {
    const chart = echarts.init(trendChart.value)
    
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: borrowTrend.value.map(item => item.date)
      },
      yAxis: {
        type: 'value',
        name: '借阅数量'
      },
      series: [
        {
          data: borrowTrend.value.map(item => item.count),
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#409eff'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(64, 158, 255, 0.5)'
              }, {
                offset: 1, color: 'rgba(64, 158, 255, 0.1)'
              }]
            }
          }
        }
      ]
    }
    
    chart.setOption(option)
    
    // 响应式调整
    window.addEventListener('resize', () => {
      chart.resize()
    })
  })
}

// 渲染借阅状态分布图表
const renderStatusChart = () => {
  if (!statusChart.value) return
  
  // 动态导入 ECharts
  import('echarts').then(echarts => {
    const chart = echarts.init(statusChart.value)
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 10,
        data: statusDistribution.value.map(item => item.name)
      },
      series: [
        {
          name: '借阅状态',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: statusDistribution.value
        }
      ]
    }
    
    chart.setOption(option)
    
    // 响应式调整
    window.addEventListener('resize', () => {
      chart.resize()
    })
  })
}
</script>

<style scoped>
.statistics {
  padding: 20px 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.overview-cards {
  margin-bottom: 20px;
}

.overview-card {
  height: 100%;
  transition: transform 0.3s, box-shadow 0.3s;
}

.overview-card:hover {
  transform: translateY(-5px);
}

.card-content {
  position: relative;
  padding: 20px;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.card-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 48px;
  opacity: 0.1;
}

.book-icon {
  color: #409eff;
}

.user-icon {
  color: #67c23a;
}

.borrow-icon {
  color: #e6a23c;
}

.overdue-icon {
  color: #f56c6c;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart {
  height: 300px;
  width: 100%;
}

.top-books, .top-users {
  padding: 10px 0;
}
</style>
