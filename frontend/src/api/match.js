import request from './request'

/** 分页查询比赛列表 */
export function fetchMatches(params) {
  return request.get('/matches', { params })
}

/** 新建比赛（状态由后端固定为未开始） */
export function createMatch(data) {
  return request.post('/matches', data)
}

/** 编辑比赛 */
export function updateMatch(id, data) {
  return request.put(`/matches/${id}`, data)
}

/** 手动切换比赛状态：pending / ongoing / finished */
export function updateMatchStatus(id, status) {
  return request.put(`/matches/${id}/status`, { status })
}

/** 删除比赛 */
export function deleteMatch(id) {
  return request.delete(`/matches/${id}`)
}
