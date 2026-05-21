<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <div class="toolbar">
      <div class="toolbar__left">
        <el-select
          v-model="query.action"
          placeholder="操作类型"
          clearable
          style="width: 180px"
          @change="handleSearch"
        >
          <el-option label="登录" value="login" />
          <el-option label="登出" value="logout" />
          <el-option label="创建" value="create" />
          <el-option label="更新" value="update" />
          <el-option label="删除" value="delete" />
          <el-option label="审批" value="approve" />
          <el-option label="其它" value="other" />
        </el-select>
        <el-input
          v-model="query.search"
          placeholder="搜索用户名 / 详情"
          clearable
          style="width: 240px; margin-left: 12px"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
      </div>
      <el-button :icon="Refresh" @click="handleSearch">刷新</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" stripe border style="width: 100%; margin-top: 16px">
      <el-table-column prop="user_name" label="操作人" width="120" />
      <el-table-column prop="action" label="操作类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="actionTagType(row.action)" size="small">{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target" label="操作目标" min-width="140" show-overflow-tooltip />
      <el-table-column prop="detail" label="详情" min-width="180" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP地址" width="150" />
      <el-table-column prop="created_at" label="操作时间" width="170" />
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>
  </div>
</template>

<script setup>
/**
 * 操作日志查询页面（只读）
 * 支持按操作类型（登录/登出/创建/更新/删除/审批）和关键词筛选日志
 * 展示操作人、操作目标、详情、IP地址和操作时间
 */
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { logAPI } from '@/api'

// ── 操作类型标签颜色映射 ──
// 根据操作类型返回对应的 Tag 颜色类型
const actionTagType = (action) => {
  const map = {
    login: 'success',
    logout: 'info',
    create: 'primary',
    update: 'warning',
    delete: 'danger',
    approve: 'success',
  }
  return map[action] || 'info'
}

// ── 列表数据与分页 ──
const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, search: '', action: '' })

// 搜索时重置到第一页
function handleSearch() {
  query.page = 1
  fetchData()
}

// 从后端获取日志列表（支持分页、关键词和操作类型筛选）
async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.search) params.search = query.search
    if (query.action) params.action = query.action
    const res = await logAPI.list(params)
    list.value = res.data?.results || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchData())
</script>

<style>
.toolbar {
  display: flex; justify-content: space-between; align-items: center;
}

.toolbar__left {
  display: flex; align-items: center;
}

.pagination-wrap {
  display: flex; justify-content: flex-end; margin-top: 16px;
}
</style>
