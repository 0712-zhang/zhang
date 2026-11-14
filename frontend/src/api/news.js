import request from './request'

/** 分页查询新闻（按发布时间倒序） */
export function fetchNews(params) {
  return request.get('/news', { params })
}

/** 发布新闻 */
export function createNews(data) {
  return request.post('/news', data)
}

/** 编辑新闻 */
export function updateNews(id, data) {
  return request.put(`/news/${id}`, data)
}

/** 删除新闻 */
export function deleteNews(id) {
  return request.delete(`/news/${id}`)
}
