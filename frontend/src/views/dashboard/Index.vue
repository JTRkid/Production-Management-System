<template>
  <div class="page-card">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card stat-card--blue">
          <div class="stat-card__icon">
            <el-icon :size="32"><DataAnalysis /></el-icon>
          </div>
          <div class="stat-card__info">
            <div class="stat-card__label">总工单数</div>
            <div class="stat-card__value">{{ overview.total_wo ?? '-' }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-card--orange">
          <div class="stat-card__icon">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-card__info">
            <div class="stat-card__label">进行中工单</div>
            <div class="stat-card__value">{{ overview.in_progress_wo ?? '-' }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-card--green">
          <div class="stat-card__icon">
            <el-icon :size="32"><Checked /></el-icon>
          </div>
          <div class="stat-card__info">
            <div class="stat-card__label">已完成工单</div>
            <div class="stat-card__value">{{ overview.completed_wo ?? '-' }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-card--red">
          <div class="stat-card__icon">
            <el-icon :size="32"><WarningFilled /></el-icon>
          </div>
          <div class="stat-card__info">
            <div class="stat-card__label">缺陷率</div>
            <div class="stat-card__value">{{ overview.defect_rate != null ? overview.defect_rate + '%' : '-' }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <div class="card-header"><span>工单状态分布</span></div>
          </template>
          <div ref="statusChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div class="card-header"><span>近30天完成率趋势</span></div>
          </template>
          <div ref="trendChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细面板 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header"><span>月度产量</span></div>
          </template>
          <div class="detail-item">
            <span class="detail-item__label">本月完成数量</span>
            <span class="detail-item__value">{{ overview.month_completed_qty ?? '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-item__label">本月销售额</span>
            <span class="detail-item__value">{{ formatMoney(overview.month_sales_amount) }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header"><span>待处理</span></div>
          </template>
          <div class="detail-item">
            <span class="detail-item__label">逾期工单</span>
            <span class="detail-item__value" style="color: #f56c6c">{{ overview.overdue_wo ?? '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-item__label">待处理订单</span>
            <span class="detail-item__value">{{ overview.pending_orders ?? '-' }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header"><span>今日生产</span></div>
          </template>
          <div class="detail-item">
            <span class="detail-item__label">计划产量</span>
            <span class="detail-item__value">{{ dailyData.plan_qty ?? '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-item__label">实际产量</span>
            <span class="detail-item__value">{{ dailyData.actual_qty ?? '-' }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * 生产看板首页组件
 * 展示生产统计数据（总工单、进行中、已完成、缺陷率）
 * 包含工单状态分布饼图和近30天完成率趋势折线图（ECharts）
 * 底部详情面板显示月度产量、待处理事项和今日生产数据
 */
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { dashboardAPI } from '@/api'
import { DataAnalysis, TrendCharts, Checked, WarningFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ── 响应式状态 ──
const overview = ref({})        // 看板概览数据（总工单、进行中、已完成、缺陷率等）
const dailyData = ref({})       // 今日生产数据
const statusChartRef = ref(null) // 饼图 DOM 引用
const trendChartRef = ref(null)  // 折线图 DOM 引用
let statusChart = null           // 饼图 ECharts 实例
let trendChart = null            // 折线图 ECharts 实例

// ── 工具函数 ──
// 将数值格式化为人民币格式（带千分位和两位小数）
function formatMoney(val) {
  if (val == null || val === 0) return '-'
  return '¥' + Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

// ── 数据获取 ──
// 获取看板概览数据并渲染饼图
async function fetchOverview() {
  try {
    const res = await dashboardAPI.overview()
    overview.value = res.data || res || {}
    await nextTick()
    renderStatusChart()
  } catch { /* handled */ }
}

// 获取今日生产数据
async function fetchDaily() {
  try {
    const res = await dashboardAPI.prodDaily()
    dailyData.value = res.data || res || {}
  } catch { /* handled */ }
}

// 获取完成率趋势数据并渲染折线图
async function fetchTrend() {
  try {
    const res = await dashboardAPI.completionRate()
    const data = res.data || res || []
    await nextTick()
    renderTrendChart(data)
  } catch { /* handled */ }
}

// ── 图表渲染 ──
// 渲染工单状态分布饼图（待派工/进行中/已完成）
function renderStatusChart() {
  if (!statusChartRef.value) return
  if (!statusChart) statusChart = echarts.init(statusChartRef.value)
  const o = overview.value
  statusChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 12 } },
    color: ['#909399', '#E6A23C', '#409EFF', '#67C23A', '#909399'],
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{c}' },
      data: [
        { value: (o.total_wo || 0) - (o.in_progress_wo || 0) - (o.completed_wo || 0), name: '待派工' },
        { value: o.in_progress_wo || 0, name: '进行中' },
        { value: o.completed_wo || 0, name: '已完成' },
      ],
    }],
  })
}

// 渲染近14天完成率趋势折线图（带渐变面积）
function renderTrendChart(data) {
  if (!trendChartRef.value) return
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)
  // Only show last 14 days for readability
  const recent = data.slice(-14)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: recent.map(d => d.date.slice(5)),
      axisLabel: { fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { formatter: '{value}%', fontSize: 11 },
    },
    series: [{
      type: 'line',
      data: recent.map(d => d.completion_rate),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 3, color: '#409EFF' },
      itemStyle: { color: '#409EFF' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64,158,255,0.3)' },
          { offset: 1, color: 'rgba(64,158,255,0.02)' },
        ]),
      },
    }],
  })
}

// ── 生命周期 ──
// 窗口大小变化时重新调整图表尺寸
function handleResize() {
  statusChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  fetchOverview()
  fetchDaily()
  fetchTrend()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  statusChart?.dispose()
  trendChart?.dispose()
})
</script>

<style>
.stat-row { margin-bottom: 8px; }

.stat-card {
  display: flex; align-items: center; gap: 16px;
  padding: 20px; border-radius: 8px; color: #fff;
}
.stat-card--blue   { background: linear-gradient(135deg, #409eff, #337ecc); }
.stat-card--orange { background: linear-gradient(135deg, #e6a23c, #d48806); }
.stat-card--green  { background: linear-gradient(135deg, #67c23a, #529b2e); }
.stat-card--red    { background: linear-gradient(135deg, #f56c6c, #c45656); }

.stat-card__icon { flex-shrink: 0; opacity: 0.8; }
.stat-card__label { font-size: 13px; opacity: 0.85; margin-bottom: 6px; }
.stat-card__value { font-size: 26px; font-weight: 700; }

.detail-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid #f0f0f0;
}
.detail-item:last-child { border-bottom: none; }
.detail-item__label { color: #909399; font-size: 14px; }
.detail-item__value { font-size: 18px; font-weight: 600; color: #303133; }

.card-header { font-size: 15px; font-weight: 600; }
</style>
