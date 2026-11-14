import { createRouter, createWebHashHistory } from 'vue-router'

import { TOKEN_KEY } from '../api/request'

const routes = [
  { path: '/', redirect: '/users' },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('../views/UserManage.vue'),
    meta: { title: '用户管理' },
  },
  {
    path: '/matches',
    name: 'matches',
    component: () => import('../views/MatchManage.vue'),
    meta: { title: '比赛管理' },
  },
  {
    path: '/news',
    name: 'news',
    component: () => import('../views/NewsManage.vue'),
    meta: { title: '新闻管理' },
  },
  {
    path: '/config',
    name: 'config',
    component: () => import('../views/ConfigManage.vue'),
    meta: { title: '系统配置' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// 全局守卫：未登录访问任何页面都跳转登录页
router.beforeEach((to) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!to.meta.public && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.path === '/login' && token) {
    return { path: '/' }
  }
  return true
})

export default router
