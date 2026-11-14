import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/users' },
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
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
