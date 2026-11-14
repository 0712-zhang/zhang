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
      <div class="toolbar-right">
        <el-button @click="handleGrant">批量发放初始资金</el-button>
        <el-button type="primary" @click="openCreate">新增用户</el-button>
      </div>
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
      <el-table-column label="报名状态" width="110" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.is_registered ? 'success' : 'info'"
            disable-transitions
          >
            {{ row.is_registered ? '已报名' : '未报名' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="资金" width="150" align="right">
        <template #default="{ row }">{{ formatMoney(row.balance) }}</template>
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
        <el-form-item label="报名状态">
          <el-switch
            v-model="form.is_registered"
            active-text="已报名"
            inactive-text="未报名"
          />
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
  grantInitialCapital,
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

const formatMoney = (value) =>
  Number(value ?? 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const total = ref(0)
const query = reactive({ keyword: '', page: 1, page_size: 10 })

const dialogVisible = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  username: '',
  role: 'user',
  is_registered: false,
})
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
  form.is_registered = false
  dialogVisible.value = true
}

function openEdit(row) {
  form.id = row.id
  form.username = row.username
  form.role = row.role
  form.is_registered = row.is_registered
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
    const payload = {
      username: form.username.trim(),
      role: form.role,
      is_registered: form.is_registered,
    }
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

async function handleGrant() {
  try {
    await ElMessageBox.confirm(
      '将按系统配置中的「初始资金」给所有普通用户发放，并覆盖其现有资金，确定继续吗？',
      '批量发放初始资金',
      { type: 'warning', confirmButtonText: '发放', cancelButtonText: '取消' },
    )
  } catch {
    return // 用户取消
  }

  const result = await grantInitialCapital()
  ElMessage.success(
    `已为 ${result.updated} 名普通用户发放 ${formatMoney(result.amount)} 元`,
  )
  await loadUsers()
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

.toolbar-right {
  display: flex;
  gap: 12px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
