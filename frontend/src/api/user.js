import request from './request'

/** 分页查询用户列表 */
export function fetchUsers(params) {
  return request.get('/users', { params })
}

/** 新增用户 */
export function createUser(data) {
  return request.post('/users', data)
}

/** 编辑用户 */
export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

/** 删除用户 */
export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

/** 给所有普通用户批量发放初始资金 */
export function grantInitialCapital() {
  return request.post('/users/grant-initial-capital')
}
