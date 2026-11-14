import request from './request'

/** 管理员登录，成功后返回 access_token */
export function login(data) {
  return request.post('/auth/login', data)
}

/** 获取当前登录用户信息（用于校验 Token 是否有效） */
export function fetchMe() {
  return request.get('/auth/me')
}
