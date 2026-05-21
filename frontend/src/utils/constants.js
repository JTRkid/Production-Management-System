/** 共享常量 — 生产管理系统 */

// 角色中文映射
export const roleMap = {
  admin: '系统管理员',
  planner: '生产计划员',
  workshop_director: '车间主任',
  foreman: '班组长',
  worker: '工人',
  inspector: '质检员',
  storekeeper: '库管员',
  salesman: '业务员',
  purchaser: '采购员',
}

// 状态颜色映射
export const statusColorMap = {
  draft: 'info', approved: 'warning', released: 'primary',
  completed: 'success', cancelled: 'danger', dispatched: 'warning',
  in_progress: 'primary', in_production: 'primary',
  pending: 'info', closed: 'info',
  shipped: 'success', received: 'success',
  ordered: 'warning', partial_received: 'primary',
  pass: 'success', fail: 'danger', concession: 'warning',
  normal: 'success', maintenance: 'warning', scrapped: 'danger',
}

// 物料类型映射
export const materialTypeMap = { raw: '原材料', semi: '半成品', finished: '成品' }

// 时间格式化
export function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}

export function formatDate(t) {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}
