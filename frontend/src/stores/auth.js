/**
 * 认证状态管理 — Pinia Store
 *
 * 管理用户登录状态、JWT Token 和用户信息。
 * 数据持久化到 sessionStorage，刷新页面后自动恢复登录态。
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api'

export const useAuthStore = defineStore('auth', () => {
  // ── 状态：从 sessionStorage 恢复，避免刷新后丢失 ──
  const user = ref(JSON.parse(sessionStorage.getItem('user') || 'null'))
  const token = ref(sessionStorage.getItem('access_token') || '')
  const refreshToken = ref(sessionStorage.getItem('refresh_token') || '')

  // ── 计算属性 ──
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  /** 角色中文名称映射 */
  const roleLabel = computed(() => {
    const map = {
      admin: '管理员', planner: '计划员', workshop_director: '车间主任',
      foreman: '班组长', worker: '工人', inspector: '质检员',
      storekeeper: '库管员', salesman: '业务员', purchaser: '采购员',
    }
    return map[user.value?.role] || '未知'
  })

  /** 登录：保存 token 和用户信息到 state + sessionStorage */
  function login(data) {
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    user.value = data.user
    sessionStorage.setItem('access_token', data.access_token)
    sessionStorage.setItem('refresh_token', data.refresh_token)
    sessionStorage.setItem('user', JSON.stringify(data.user))
  }

  /** 登出：清除所有状态和持久化数据 */
  function logout() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    sessionStorage.clear()
  }

  return { user, token, refreshToken, isLoggedIn, isAdmin, roleLabel, login, logout }
})
