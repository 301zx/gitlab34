<template>
  <div class="admin-layout">
    <el-container>
      <el-header class="admin-header">
        <div class="header-content">
          <h2>管理员控制台</h2>
          <div class="header-actions">
          <el-button @click="$router.push('/')">
            <el-icon><House /></el-icon>
            返回首页
          </el-button>
        </div>
        </div>
      </el-header>

      <el-container>
        <el-aside width="250px" class="admin-sidebar">
          <el-menu
            :default-active="activeMenu"
            class="admin-menu"
            router
          >
            <el-menu-item index="/admin">
              <el-icon><DataBoard /></el-icon>
              <span>仪表板</span>
            </el-menu-item>
            
            <el-menu-item index="/admin/users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            
            <el-menu-item index="/admin/books">
              <el-icon><Reading /></el-icon>
              <span>图书管理</span>
            </el-menu-item>
            
            <el-menu-item index="/admin/categories">
              <el-icon><CollectionTag /></el-icon>
              <span>分类管理</span>
            </el-menu-item>
            
            <el-menu-item index="/admin/borrows">
              <el-icon><DocumentCopy /></el-icon>
              <span>借阅管理</span>
            </el-menu-item>
            
            <el-menu-item index="/admin/statistics">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据统计</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main class="admin-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  House,
  DataBoard,
  User,
  Reading,
  CollectionTag,
  DocumentCopy,
  DataAnalysis,
  Document
} from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => {
  return route.path
})
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.admin-header {
  background: #409eff;
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-content h2 {
  margin: 0;
}

.admin-sidebar {
  background: #fff;
  border-right: 1px solid #e6e6e6;
}

.admin-menu {
  border: none;
  height: 100%;
}

.admin-main {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>