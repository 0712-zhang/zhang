<template>
  <el-card v-loading="loading" shadow="never" class="config-card">
    <template #header>
      <span>系统与赛制配置</span>
    </template>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      @submit.prevent
    >
      <el-form-item label="初始资金" prop="initial_capital">
        <el-input-number
          v-model="form.initial_capital"
          :min="0.01"
          :step="10000"
          :precision="2"
          style="width: 220px"
        />
        <span class="unit">元</span>
      </el-form-item>

      <el-form-item label="手续费率">
        <el-input-number
          v-model="form.commission_rate"
          :min="0"
          :max="100"
          :step="0.01"
          :precision="4"
          style="width: 220px"
        />
        <span class="unit">%</span>
      </el-form-item>

      <el-form-item label="印花税率">
        <el-input-number
          v-model="form.stamp_duty_rate"
          :min="0"
          :max="100"
          :step="0.01"
          :precision="4"
          style="width: 220px"
        />
        <span class="unit">%</span>
      </el-form-item>

      <el-form-item label="比赛总时长" prop="total_duration">
        <el-input-number
          v-model="form.total_duration"
          :min="1"
          :max="1440"
          style="width: 220px"
        />
        <span class="unit">分钟</span>
      </el-form-item>

      <el-form-item label="每回合时长" prop="round_duration">
        <el-input-number
          v-model="form.round_duration"
          :min="1"
          :max="600"
          style="width: 220px"
        />
        <span class="unit">分钟</span>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存配置
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchConfig, saveConfig } from '../api/config'

const loading = ref(false)
const saving = ref(false)
const formRef = ref()
const form = reactive({
  initial_capital: 0,
  commission_rate: 0,
  stamp_duty_rate: 0,
  total_duration: 60,
  round_duration: 5,
})

const validateInitialCapital = (rule, value, callback) => {
  if (value === null || value === undefined || value === '') {
    return callback(new Error('请输入初始资金'))
  }
  if (Number(value) <= 0) {
    return callback(new Error('初始资金必须是正数'))
  }
  callback()
}

const validateTotalDuration = (rule, value, callback) => {
  const round = form.round_duration
  if (!value || !round) return callback()
  if (value % round !== 0) {
    return callback(new Error('比赛总时长必须是每回合时长的整数倍'))
  }
  callback()
}

const rules = {
  initial_capital: [
    { validator: validateInitialCapital, trigger: 'change' },
  ],
  total_duration: [{ validator: validateTotalDuration, trigger: 'change' }],
}

// 每回合时长变化后，重新校验总时长是否仍为整数倍
watch(
  () => form.round_duration,
  () => {
    if (form.total_duration) {
      formRef.value?.validateField('total_duration').catch(() => {})
    }
  },
)

async function loadConfig() {
  loading.value = true
  try {
    const data = await fetchConfig()
    Object.assign(form, {
      initial_capital: data.initial_capital,
      commission_rate: data.commission_rate,
      stamp_duty_rate: data.stamp_duty_rate,
      total_duration: data.total_duration,
      round_duration: data.round_duration,
    })
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    // 校验失败：弹出提示并阻止提交
    if (form.total_duration % form.round_duration !== 0) {
      ElMessage.error('比赛总时长必须是每回合时长的整数倍')
    } else {
      ElMessage.error('请检查配置项填写是否正确')
    }
    return
  }

  saving.value = true
  try {
    await saveConfig({ ...form })
    ElMessage.success('配置已保存')
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.config-card {
  max-width: 720px;
}

.unit {
  margin-left: 8px;
  color: #909399;
  font-size: 13px;
}
</style>
