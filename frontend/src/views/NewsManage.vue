<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>新闻列表</span>
        <el-button type="primary" @click="openCreate">发布新闻</el-button>
      </div>
    </template>

    <el-table v-loading="loading" :data="items" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
      <el-table-column prop="content" label="内容" min-width="280" show-overflow-tooltip />
      <el-table-column label="发布时间" width="180">
        <template #default="{ row }">{{ formatTime(row.published_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadNews"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑新闻' : '发布新闻'"
      width="600px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="请输入新闻内容"
          />
        </el-form-item>
        <el-form-item label="发布时间">
          <el-date-picker
            v-model="form.published_at"
            type="datetime"
            placeholder="默认当前时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { createNews, deleteNews, fetchNews, updateNews } from '../api/news'

const loading = ref(false)
const saving = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10

const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()
const form = reactive({ title: '', content: '', published_at: null })

const rules = {
  title: [{ required: true, message: '请输入新闻标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入新闻内容', trigger: 'blur' }],
}

function formatTime(value) {
  if (!value) return ''
  return value.replace('T', ' ').slice(0, 19)
}

async function loadNews() {
  loading.value = true
  try {
    const data = await fetchNews({ page: page.value, page_size: pageSize })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  form.title = ''
  form.content = ''
  form.published_at = null
  formRef.value?.clearValidate()
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.title = row.title
  form.content = row.content
  form.published_at = row.published_at
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = { ...form }
    if (editingId.value) {
      await updateNews(editingId.value, payload)
      ElMessage.success('新闻已更新')
    } else {
      await createNews(payload)
      ElMessage.success('新闻已发布')
      page.value = 1
    }
    dialogVisible.value = false
    await loadNews()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  const confirmed = await ElMessageBox.confirm(
    `确定删除新闻「${row.title}」吗？`,
    '删除确认',
    { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
  ).catch(() => false)
  if (!confirmed) return

  await deleteNews(row.id)
  ElMessage.success('新闻已删除')
  // 删除最后一条时回退一页
  if (items.value.length === 1 && page.value > 1) {
    page.value -= 1
  }
  await loadNews()
}

onMounted(loadNews)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
