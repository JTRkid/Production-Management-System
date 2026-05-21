<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <el-form :model="query" inline>
      <el-form-item label="工单号">
        <el-input v-model="query.work_order" placeholder="输入工单号" clearable style="width:200px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
        <el-button type="warning" @click="fetchMyReports">我的报工</el-button>
      </el-form-item>
    </el-form>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="work_order_wo_no" label="工单号" min-width="140" />
      <el-table-column prop="route_step_name" label="工序" min-width="130" />
      <el-table-column prop="worker_name" label="报工人" width="100" />
      <el-table-column prop="report_quantity" label="合格数量" width="90" align="right" />
      <el-table-column prop="defect_quantity" label="缺陷数量" width="90" align="right" />
      <el-table-column prop="work_hours" label="工时" width="80" align="right" />
      <el-table-column prop="report_time" label="报工时间" width="160" />
      <el-table-column prop="remark" label="备注" min-width="160" />
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      style="margin-top:16px; justify-content:flex-end"
      @current-change="fetchData"
      @size-change="fetchData"
    />
  </div>
</template>

<script setup>
/**
 * 报工记录查询页面（只读）
 * 展示所有生产报工记录，支持按工单号筛选，
 * 可切换查看"全部报工"或"我的报工"两种视图。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { workReportAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)        // 列表加载状态
const list = ref([])              // 报工记录列表
const total = ref(0)              // 总记录数
const isMyReports = ref(false)    // 是否处于"我的报工"模式

// ── 搜索条件 ──
const query = reactive({ page: 1, page_size: 10, work_order: '' })

// ── 数据获取 ──

/** 获取全部报工记录列表 */
async function fetchData() {
  loading.value = true
  isMyReports.value = false
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.work_order) params.work_order = query.work_order
    const res = await workReportAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

/** 获取当前用户的报工记录（"我的报工"视图） */
async function fetchMyReports() {
  loading.value = true
  isMyReports.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.work_order) params.work_order = query.work_order
    const res = await workReportAPI.myReports(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

// ── 搜索与重置 ──

/** 清空搜索条件并重新查询 */
function resetQuery() {
  query.work_order = ''
  query.page = 1
  fetchData()
}

// ── 生命周期 ──
onMounted(() => fetchData())
</script>

<style scoped>
.page-card { background: #fff; border-radius: 8px; padding: 20px; }
</style>
