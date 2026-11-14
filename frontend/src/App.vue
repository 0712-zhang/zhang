<template>
  <!-- 登录页不套后台布局 -->
  <router-view v-if="route.meta.public" />

  <el-container v-else class="layout">
    <el-aside width="220px" class="layout-aside">
      <div class="logo">管理员后台</div>
      <el-menu :default-active="route.path" router class="menu">
        <el-menu-item index="/users">用户管理</el-menu-item>
        <el-menu-item index="/matches">比赛管理</el-menu-item>
        <el-menu-item index="/news">新闻管理</el-menu-item>
        <el-menu-item index="/config">系统配置</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <h1>{{ route.meta.title }}</h1>
        <div class="header-right">
          <span class="username">{{ username }}</span>
          <el-button link type="primary" @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { TOKEN_KEY, USERNAME_KEY } from './api/request'

const route = useRoute()
const router = useRouter()

const username = computed(() => localStorage.getItem(USERNAME_KEY) || '管理员')

function handleLogout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USERNAME_KEY)
  ElMessage.success('已退出登录')
  router.replace('/login')
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.layout-aside {
  background: #fff;
  border-right: 1px solid #ebeef5;
}

.logo {
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 24px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #ebeef5;
}

.menu {
  border-right: none;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.layout-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
  color: #606266;
}
</style>
