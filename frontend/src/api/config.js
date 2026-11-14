import request from './request'

/** 读取系统配置 */
export function fetchConfig() {
  return request.get('/config')
}

/** 保存系统配置 */
export function saveConfig(data) {
  return request.put('/config', data)
}
