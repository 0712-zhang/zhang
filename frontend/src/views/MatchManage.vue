<template>
  <el-card shadow="never">
    <!-- 工具栏 -->
    <div class="toolbar">
      <span class="toolbar-tip">共 {{ total }} 场比赛</span>
      <el-button type="primary" @click="openCreate">新建比赛</el-button>
    </div>

    <!-- 比赛列表 -->
    <el-table
      v-loading="loading"
      :data="matches"
      border
      stripe
      empty-text="暂无比赛，点击右上角新建"
    >
      <el-table-column prop="id" label="比赛ID" width="90" align="center" />
      <el-table-column prop="name" label="比赛名称" min-width="200" />
      <el-table-column label="状态" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" disable-transitions>
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="开始时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatTime(row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column label="当前轮次" width="110" align="center">
        <template #default="{ row }">第 {{ row.current_round }} 轮</template>
      </el-table-column>
      <el-table-column label="操作" width="280" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-dropdown
            trigger="click"
            @command="(command) => handleStatusChange(row, command)"
          >
            <el-button link type="warning">状态控制</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="item in statusOptions"
                  :key="item.value"
                  :command="item.value"
                  :disabled="row.status === item.value"
                >
                  {{ item.label }}{{ row.status === item.value ? '（当前）' : '' }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
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
        @current-change="loadMatches"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 新建 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑比赛' : '新建比赛'"
      width="520px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="90px"
        @submit.prevent
      >
        <el-form-item label="比赛名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入比赛名称（2-100 个字符）"
            maxlength="100"
            clearable
          />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="form.start_time"
            type="datetime"
            placeholder="请选择开始时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="当前轮次" prop="current_round">
          <el-input-number
            v-model="form.current_round"
            :min="1"
            :max="999"
            controls-position="right"
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item v-if="!isEdit">
          <span class="form-tip">新建后状态默认为「未开始」，可在列表中手动变更。</span>
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
  createMatch,
  deleteMatch,
  fetchMatches,
  updateMatch,
  updateMatchStatus,
} from '../api/match'

const statusOptions = [
  { value: 'pending', label: '未开始', tag: 'info' },
  { value: 'ongoing', label: '进行中', tag: 'success' },
  { value: 'finished', label: '已结束', tag: 'danger' },
]

const statusLabel = (status) =>
  statusOptions.find((item) => item.value === status)?.label ?? status
const statusTagType = (status) =>
  statusOptions.find((item) => item.value === status)?.tag ?? 'info'

// 后端返回 ISO 格式（2026-11-20T10:00:00），表格展示为空格分隔
const formatTime = (value) =>
  value ? String(value).replace('T', ' ').slice(0, 19) : '-'

const loading = ref(false)
const submitting = ref(false)
const matches = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10 })

const dialogVisible = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  name: '',
  start_time: '',
  current_round: 1,
})
const isEdit = computed(() => form.id !== null)

const rules = {
  name: [
    { required: true, message: '请输入比赛名称', trigger: 'blur' },
    { min: 2, max: 100, message: '比赛名称长度为 2-100 个字符', trigger: 'blur' },
  ],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  current_round: [{ required: true, message: '请输入当前轮次', trigger: 'change' }],
}

async function loadMatches() {
  loading.value = true
  try {
    const data = await fetchMatches({
      page: query.page,
      page_size: query.page_size,
    })
    matches.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function handleSizeChange() {
  query.page = 1
  loadMatches()
}

function openCreate() {
  form.id = null
  form.name = ''
  form.start_time = ''
  form.current_round = 1
  dialogVisible.value = true
}

function openEdit(row) {
  form.id = row.id
  form.name = row.name
  form.start_time = formatTime(row.start_time)
  form.current_round = row.current_round
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
      name: form.name.trim(),
      start_time: form.start_time,
      current_round: form.current_round,
    }
    if (isEdit.value) {
      await updateMatch(form.id, payload)
      ElMessage.success('编辑成功')
    } else {
      await createMatch(payload)
      ElMessage.success('新建成功，比赛状态为「未开始」')
    }
    dialogVisible.value = false
    await loadMatches()
  } finally {
    submitting.value = false
  }
}

async function handleStatusChange(row, status) {
  // 状态完全由管理员手动指定，不做任何基于时间的自动判断
  await updateMatchStatus(row.id, status)
  ElMessage.success(`已将「${row.name}」状态改为「${statusLabel(status)}」`)
  await loadMatches()
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除比赛「${row.name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return // 用户取消
  }

  await deleteMatch(row.id)
  ElMessage.success('删除成功')
  if (matches.value.length === 1 && query.page > 1) {
    query.page -= 1
  }
  await loadMatches()
}

onMounted(loadMatches)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.toolbar-tip {
  color: #909399;
  font-size: 13px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.form-tip {
  color: #909399;
  font-size: 12px;
}
</style>
