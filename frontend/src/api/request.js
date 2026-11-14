import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 响应拦截：直接返回 data，并统一提示后端错误信息
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const detail = error.response?.data?.detail
    let message = '请求失败，请稍后重试'
    if (typeof detail === 'string') {
      message = detail
    } else if (Array.isArray(detail)) {
      // Pydantic 校验错误
      message = detail.map((item) => item.msg).join('；')
    }
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export default request
