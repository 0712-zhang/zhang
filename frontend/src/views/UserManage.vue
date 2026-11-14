<template>
  <el-card shadow="never">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="query.keyword"
          placeholder="请输入用户名"
          clearable
          style="width: 240px"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" plain @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
      <el-button type="primary" @click="openCreate">新增用户</el-button>
    </div>

    <!-- 用户列表 -->
    <el-table
      v-loading="loading"
      :data="users"
      border
      stripe
      empty-text="暂无数据"
    >
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="username" label="用户名" min-width="160" />
      <el-table-column label="角色" width="140" align="center">
        <template #default="{ row }">
          <el-tag :type="roleTagType(row.role)" disable-transitions>
            {{ roleLabel(row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="loadUsers"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      width="480px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        @submit.prevent
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名（2-50 个字符）"
            maxlength="50"
            clearable
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option
              v-for="item in roleOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createUser,
  deleteUser,
  fetchUsers,
  updateUser,
} from '../api/user'

const roleOptions = [
  { value: 'admin', label: '管理员', tag: 'danger' },
  { value: 'editor', label: '编辑', tag: 'warning' },
  { value: 'user', label: '普通用户', tag: 'info' },
]

const roleLabel = (role) =>
  roleOptions.find((item) => item.value === role)?.label ?? role
const roleTagType = (role) =>
  roleOptions.find((item) => item.value === role)?.tag ?? 'info'

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const total = ref(0)
const query = reactive({ keyword: '', page: 1, page_size: 10 })

const dialogVisible = ref(false)
const formRef = ref()
const form = reactive({ id: null, username: '', role: 'user' })
const isEdit = computed(() => form.id !== null)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度为 2-50 个字符', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

async function loadUsers() {
  loading.value = true
  try {
    const data = await fetchUsers({
      keyword: query.keyword || undefined,
      page: query.page,
      page_size: query.page_size,
    })
    users.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  loadUsers()
}

function handleReset() {
  query.keyword = ''
  handleSearch()
}

function handleSizeChange() {
  query.page = 1
  loadUsers()
}

function openCreate() {
  form.id = null
  form.username = ''
  form.role = 'user'
  dialogVisible.value = true
}

function openEdit(row) {
  form.id = row.id
  form.username = row.username
  form.role = row.role
  dialogVisible.value = true
}

function handleDialogClosed() {
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = { username: form.username.trim(), role: form.role }
    if (isEdit.value) {
      await updateUser(form.id, payload)
      ElMessage.success('编辑成功')
    } else {
      await createUser(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await loadUsers()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定删除用户「${row.username}」吗？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return // 用户取消
  }

  await deleteUser(row.id)
  ElMessage.success('删除成功')
  // 删除当前页最后一条时回退一页
  if (users.value.length === 1 && query.page > 1) {
    query.page -= 1
  }
  await loadUsers()
}

onMounted(loadUsers)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
