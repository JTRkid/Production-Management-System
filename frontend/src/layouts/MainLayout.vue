<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo" @click="$router.push('/dashboard')">
        <el-icon :size="22"><Setting /></el-icon>
        <span v-show="!isCollapse" class="logo-text">生产管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        background-color="#1a1a2e"
        text-color="#a0aec0"
        active-text-color="#409EFF"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>生产看板</span>
        </el-menu-item>

        <el-sub-menu index="sys-admin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/sys-admin/users">用户管理</el-menu-item>
          <el-menu-item index="/sys-admin/workshops">车间管理</el-menu-item>
          <el-menu-item index="/sys-admin/logs">操作日志</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="business">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>业务管理</span>
          </template>
          <el-menu-item index="/business/customers">客户管理</el-menu-item>
          <el-menu-item index="/business/sales-orders">销售订单</el-menu-item>
          <el-menu-item index="/business/suppliers">供应商管理</el-menu-item>
          <el-menu-item index="/business/purchase-orders">采购订单</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="base-data">
          <template #title>
            <el-icon><Collection /></el-icon>
            <span>基础数据</span>
          </template>
          <el-menu-item index="/base-data/materials">物料主数据</el-menu-item>
          <el-menu-item index="/base-data/bom">BOM管理</el-menu-item>
          <el-menu-item index="/base-data/routes">工艺路线</el-menu-item>
          <el-menu-item index="/base-data/work-centers">工作中心</el-menu-item>
          <el-menu-item index="/base-data/equipment">设备台账</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/prod-plan/plans">
          <el-icon><Calendar /></el-icon>
          <span>生产计划</span>
        </el-menu-item>

        <el-menu-item index="/work-order/list">
          <el-icon><Tickets /></el-icon>
          <span>工单管理</span>
        </el-menu-item>

        <el-sub-menu index="prod-track">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>过程跟踪</span>
          </template>
          <el-menu-item index="/prod-track/reports">报工记录</el-menu-item>
          <el-menu-item index="/prod-track/kanban">生产看板</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="quality">
          <template #title>
            <el-icon><Checked /></el-icon>
            <span>质量管理</span>
          </template>
          <el-menu-item index="/quality/standards">检验标准</el-menu-item>
          <el-menu-item index="/quality/inspections">检验记录</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="inventory">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="/inventory/warehouses">仓库管理</el-menu-item>
          <el-menu-item index="/inventory/stock">库存查询</el-menu-item>
          <el-menu-item index="/inventory/transactions">出入库记录</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/dashboard/reports">
          <el-icon><PieChart /></el-icon>
          <span>生产报表</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主体 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" :size="20" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag size="small" effect="plain">{{ auth.roleLabel }}</el-tag>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              {{ auth.user?.name || '用户' }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <!-- 修改密码弹窗 -->
  <el-dialog v-model="pwdDialog" title="修改密码" width="400px">
    <el-form :model="pwdForm" label-width="80px">
      <el-form-item label="旧密码">
        <el-input v-model="pwdForm.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="pwdForm.new_password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="pwdDialog = false">取消</el-button>
      <el-button type="primary" @click="changePassword">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
/**
 * 主布局组件
 * 包含：左侧菜单栏（可折叠）+ 顶部导航栏（面包屑/用户信息）+ 内容区 router-view
 */
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

// ── 侧边栏折叠状态 ──
const isCollapse = ref(false)

// ── 修改密码弹窗 ──
const pwdDialog = ref(false)
const pwdForm = ref({ old_password: '', new_password: '' })

/** 当前路由路径，用于高亮侧边栏菜单项 */
const activeMenu = computed(() => route.path)

/** 菜单点击导航（el-menu 的 router 属性在 Vue Router 4 下有兼容问题，改用手动导航） */
function handleMenuSelect(index) {
  router.push(index)
}

/** 顶部下拉菜单命令处理：退出登录 / 修改密码 */
function handleCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  } else if (cmd === 'password') {
    pwdForm.value = { old_password: '', new_password: '' }
    pwdDialog.value = true
  }
}

/** 提交修改密码，成功后强制重新登录 */
async function changePassword() {
  if (!pwdForm.value.old_password || !pwdForm.value.new_password) {
    ElMessage.warning('请填写完整')
    return
  }
  try {
    await authAPI.changePassword(pwdForm.value)
    ElMessage.success('密码修改成功，请重新登录')
    pwdDialog.value = false
    auth.logout()
    router.push('/login')
  } catch { /* handled by interceptor */ }
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.aside { background-color: #1a1a2e; overflow-y: auto; }
.logo { display: flex; align-items: center; gap: 8px; padding: 16px 20px; color: #fff; cursor: pointer; }
.logo-text { font-size: 16px; font-weight: 600; white-space: nowrap; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e4e7ed; height: 56px; padding: 0 16px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.collapse-btn { cursor: pointer; color: #606266; }
.header-right { display: flex; align-items: center; gap: 12px; }
.user-info { cursor: pointer; display: flex; align-items: center; gap: 4px; }
.main-content { background: #f0f2f5; padding: 16px; min-height: calc(100vh - 56px); }
</style>
