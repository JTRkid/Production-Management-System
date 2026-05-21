<template>
  <div class="page-card">
    <!-- 今日生产统计卡片 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">今日计划产量</div>
          <div class="stat-value">{{ dailyStats.planned_qty || 0 }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">今日完成产量</div>
          <div class="stat-value" style="color:#67c23a">{{ dailyStats.completed_qty || 0 }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">在制工单数</div>
          <div class="stat-value" style="color:#409eff">{{ dailyStats.active_orders || 0 }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">今日合格率</div>
          <div class="stat-value" style="color:#e6a23c">{{ dailyStats.pass_rate ? (dailyStats.pass_rate * 100).toFixed(1) + '%' : '--' }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 最近报工记录 -->
    <h3 style="margin-bottom:12px;font-size:16px">最近报工记录</h3>
    <el-table :data="recentReports" v-loading="loading" border stripe size="small">
      <el-table-column prop="work_order_wo_no" label="工单号" width="140" />
      <el-table-column prop="route_step_name" label="工序" width="130" />
      <el-table-column prop="worker_name" label="报工人" width="100" />
      <el-table-column prop="report_quantity" label="合格" width="70" align="right" />
      <el-table-column prop="defect_quantity" label="缺陷" width="70" align="right" />
      <el-table-column prop="work_hours" label="工时" width="70" align="right" />
      <el-table-column prop="report_time" label="报工时间" width="160" />
      <el-table-column prop="remark" label="备注" min-width="120" />
    </el-table>
  </div>
</template>

<script setup>
/**
 * 生产看板页面
 * 以数据卡片 + 最近报工记录的形式展示当日生产概况，
 * 包括计划产量、完成产量、在制工单数、合格率等核心指标。
 * 数据每 30 秒自动刷新，适用于车间大屏展示。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { dashboardAPI, workReportAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)                // 数据加载状态
const recentReports = ref([])             // 最近报工记录（最多 20 条）
const dailyStats = reactive({             // 今日生产统计数据
  planned_qty: 0,     // 计划产量
  completed_qty: 0,   // 完成产量
  active_orders: 0,   // 在制工单数
  pass_rate: 0,       // 合格率（0~1）
})

let timer = null  // 自动刷新定时器

// ── 数据获取 ──

/**
 * 并行加载生产统计和最近报工记录
 * 使用 Promise.allSettled 保证任一接口失败不影响另一个的数据展示
 */
async function loadData() {
  loading.value = true
  try {
    const [statsRes, reportsRes] = await Promise.allSettled([
      dashboardAPI.prodDaily(),
      workReportAPI.list({ page: 1, page_size: 20 }),
    ])

    // 更新生产统计卡片数据
    if (statsRes.status === 'fulfilled') {
      const data = statsRes.value.data || statsRes.value
      Object.assign(dailyStats, {
        planned_qty: data.planned_qty ?? 0,
        completed_qty: data.completed_qty ?? 0,
        active_orders: data.active_orders ?? 0,
        pass_rate: data.pass_rate ?? 0,
      })
    }

    // 更新最近报工记录表格
    if (reportsRes.status === 'fulfilled') {
      const rdata = reportsRes.value.data || reportsRes.value
      recentReports.value = (rdata.results || rdata || []).slice(0, 20)
    }
  } catch { /* ignore */ }
  finally { loading.value = false }
}

// ── 生命周期 ──

// 组件挂载时加载数据，并启动 30 秒自动刷新定时器
onMounted(() => {
  loadData()
  timer = setInterval(loadData, 30000)
})

// 组件卸载时清除定时器，避免内存泄漏
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.page-card { background: #fff; border-radius: 8px; padding: 20px; }

.stat-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}
</style>
