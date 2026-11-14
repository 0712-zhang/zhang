import axios from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'admin_token'
const USERNAME_KEY = 'admin_username'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截：自动携带 JWT
request.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
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

    // 未登录 / Token 失效：清除本地登录态并跳转登录页
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USERNAME_KEY)
      if (!window.location.hash.startsWith('#/login')) {
        window.location.hash = '#/login'
      }
    }

    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export { TOKEN_KEY, USERNAME_KEY }
export default request
