<template>
  <el-container class="layout">
    <el-aside width="220px" class="layout-aside">
      <div class="logo">管理员后台</div>
      <el-menu :default-active="route.path" router class="menu">
        <el-menu-item index="/users">用户管理</el-menu-item>
        <el-menu-item index="/matches">比赛管理</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <h1>{{ route.meta.title }}</h1>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
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
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.layout-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
</style>
