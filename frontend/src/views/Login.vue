<template>
  <div class="login-page">
    <el-card class="login-card" shadow="always">
      <div class="login-title">管理员后台</div>
      <div class="login-subtitle">请使用管理员账号登录</div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="账号" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入管理员账号"
            autocomplete="username"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-button
          type="primary"
          class="login-button"
          :loading="loading"
          native-type="submit"
        >
          登 录
        </el-button>
      </el-form>

      <div class="login-tip">默认管理员账号：admin / admin123</div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { login } from '../api/auth'
import { TOKEN_KEY, USERNAME_KEY } from '../api/request'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const formRef = ref()
const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const data = await login({ ...form })
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(USERNAME_KEY, data.username)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect
    router.replace(typeof redirect === 'string' && redirect ? redirect : '/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1f2d3d 0%, #3a4d63 100%);
}

.login-card {
  width: 380px;
  padding: 8px 12px 4px;
  border-radius: 10px;
}

.login-title {
  font-size: 22px;
  font-weight: 700;
  text-align: center;
  color: #303133;
}

.login-subtitle {
  margin: 8px 0 24px;
  font-size: 13px;
  text-align: center;
  color: #909399;
}

.login-button {
  width: 100%;
  margin-top: 4px;
}

.login-tip {
  margin-top: 16px;
  font-size: 12px;
  text-align: center;
  color: #a8abb2;
}
</style>
