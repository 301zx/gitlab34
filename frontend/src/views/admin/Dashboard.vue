<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2>系统仪表板</h2>
      <p>欢迎回来，{{ authStore.user?.username }}！今天是 {{ currentDate }}</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon users">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalUsers }}</div>
                <div class="stat-label">总用户数</div>
                <div class="stat-change">
                  <span class="change-up">+{{ stats.newUsersToday }} 今日新增</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon books">
                <el-icon><Reading /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalBooks }}</div>
                <div class="stat-label">图书总数</div>
                <div class="stat-change">
                  <span class="change-up">+{{ stats.newBooksToday }} 今日新增</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon borrows">
                <el-icon><DocumentCopy /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.currentBorrows }}</div>
                <div class="stat-label">当前借阅</div>
                <div class="stat-change">
                  <span class="change-down">{{ stats.overdueBorrows }} 逾期</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon revenue">
                <el-icon><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">¥{{ stats.totalRevenue }}</div>
                <div class="stat-label">累计收入</div>
                <div class="stat-change">
                  <span class="change-up">¥{{ stats.todayRevenue }} 今日</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <el-card>
            <template #header>
              <h3>借阅趋势</h3>
            </template>
            <div ref="borrowChart" style="height: 300px;"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12">
          <el-card>
            <template #header>
              <h3>图书分类分布</h3>
            </template>
            <div ref="categoryChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-card>
        <template #header>
          <h3>快速操作</h3>
        </template>
        <div class="action-buttons">
          <el-button type="primary" @click="$router.push('/admin/books')">
            <el-icon><Plus /></el-icon>
            添加图书
          </el-button>
          <el-button type="success" @click="$router.push('/admin/users')">
            <el-icon><User /></el-icon>
            用户管理
          </el-button>
          <el-button type="warning" @click="$router.push('/admin/borrows')">
            <el-icon><DocumentCopy /></el-icon>
            借阅管理
          </el-button>
          <el-button type="info" @click="handleSystemSettings">
            <el-icon><Setting /></el-icon>
            系统设置
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activities">
      <el-card>
        <template #header>
          <h3>最近活动</h3>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :timestamp="formatTime(activity.timestamp)"
            :type="getActivityType(activity.type)"
          >
            <div class="activity-item">
              <div class="activity-content">
                <span class="activity-user">{{ activity.user }}</span>
                <span class="activity-action">{{ activity.action }}</span>
                <span class="activity-target">{{ activity.target }}</span>
              </div>
              <div class="activity-time">{{ formatRelativeTime(activity.timestamp) }}</div>
            </div>
          </el-timeline-item>
        </el-timeline>
        <div class="view-all">
          <el-button text @click="$router.push('/admin/activities')">
            查看全部活动
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, Reading, DocumentCopy, Money, Plus, Setting 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import * as echarts from 'echarts'

const authStore = useAuthStore()
const router = useRouter()

const currentDate = ref('')
const borrowChart = ref()
const categoryChart = ref()

let borrowChartInstance = null
let categoryChartInstance = null

const stats = reactive({
  totalUsers: 0,
  newUsersToday: 0,
  totalBooks: 0,
  newBooksToday: 0,
  currentBorrows: 0,
  overdueBorrows: 0,
  totalRevenue: 0,
  todayRevenue: 0
})

const recentActivities = ref([
  {
    id: 1,
    user: '张三',
    action: '借阅了',
    target: '《Vue.js设计与实现》',
    type: 'borrow',
    timestamp: new Date(Date.now() - 1000 * 60 * 5) // 5分钟前
  },
  {
    id: 2,
    user: '李四',
    action: '归还了',
    target: '《Python编程从入门到实践》',
    type: 'return',
    timestamp: new Date(Date.now() - 1000 * 60 * 30) // 30分钟前
  },
  {
    id: 3,
    user: 'admin',
    action: '添加了',
    target: '新图书《JavaScript高级程序设计》',
    type: 'add',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2小时前
  }
])

// 初始化日期
const initDate = () => {
  const now = new Date()
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 模拟数据
    stats.totalUsers = 156
    stats.newUsersToday = 3
    stats.totalBooks = 892
    stats.newBooksToday = 5
    stats.currentBorrows = 47
    stats.overdueBorrows = 2
    stats.totalRevenue = 1280.50
    stats.todayRevenue = 45.00
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

// 初始化图表
const initCharts = () => {
  // 借阅趋势图表
  borrowChartInstance = echarts.init(borrowChart.value)
  const borrowOption = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '借阅量',
        type: 'line',
        data: [120, 132, 101, 134, 90, 230, 210],
        smooth: true,
        lineStyle: {
          width: 3
        }
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  }
  borrowChartInstance.setOption(borrowOption)

  // 分类分布图表
  categoryChartInstance = echarts.init(categoryChart.value)
  const categoryOption = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '图书分类',
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
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 235, name: '文学' },
          { value: 274, name: '科技' },
          { value: 180, name: '历史' },
          { value: 123, name: '艺术' },
          { value: 80, name: '教育' }
        ]
      }
    ]
  }
  categoryChartInstance.setOption(categoryOption)
}

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化相对时间
const formatRelativeTime = (timestamp) => {
  const now = new Date()
  const diff = now - new Date(timestamp)
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

// 获取活动类型
const getActivityType = (type) => {
  const types = {
    borrow: 'primary',
    return: 'success',
    add: 'warning'
  }
  return types[type] || 'info'
}

// 系统设置
const handleSystemSettings = () => {
  ElMessage.info('系统设置功能开发中')
}

// 响应式调整图表大小
const handleResize = () => {
  if (borrowChartInstance) {
    borrowChartInstance.resize()
  }
  if (categoryChartInstance) {
    categoryChartInstance.resize()
  }
}

onMounted(() => {
  initDate()
  loadStats()
  
  // 等待DOM渲染完成后再初始化图表
  setTimeout(() => {
    initCharts()
  }, 100)

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (borrowChartInstance) {
    borrowChartInstance.dispose()
  }
  if (categoryChartInstance) {
    categoryChartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.dashboard-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.stats-grid {
  margin-bottom: 30px;
}

.stat-card {
  border-radius: 8px;
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.stat-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.books {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.borrows {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.revenue {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-change {
  font-size: 12px;
}

.change-up {
  color: #67c23a;
}

.change-down {
  color: #f56c6c;
}

.charts-section {
  margin-bottom: 30px;
}

.quick-actions {
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.recent-activities .activity-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.activity-content {
  flex: 1;
}

.activity-user {
  font-weight: 500;
  color: #409eff;
}

.activity-action {
  margin: 0 8px;
  color: #606266;
}

.activity-target {
  font-weight: 500;
  color: #303133;
}

.activity-time {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.view-all {
  text-align: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
}
</style>