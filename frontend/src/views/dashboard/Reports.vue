<template>
  <div class="page-card">
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane label="生产日报" name="daily">
        <el-card shadow="never" v-loading="loading">
          <template #header>
            <div class="report-header">
              <span>今日生产数据 — {{ dailyData.date || '-' }}</span>
              <el-button link type="primary" @click="fetchDaily" :icon="Refresh">刷新</el-button>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6" v-for="item in dailyCards" :key="item.label">
              <div class="metric-card">
                <div class="metric-card__label">{{ item.label }}</div>
                <div class="metric-card__value">{{ item.value }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="工单完成率" name="completion">
        <el-card shadow="never" v-loading="crLoading">
          <template #header>
            <div class="report-header">
              <span>近30天工单完成率趋势</span>
            </div>
          </template>
          <el-table :data="completionData" size="small" max-height="480">
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="total_wo" label="累计工单" />
            <el-table-column prop="completed_wo" label="已完成" />
            <el-table-column label="完成率">
              <template #default="{ row }">
                <div style="display:flex;align-items:center;gap:8px">
                  <el-progress :percentage="row.completion_rate" :stroke-width="16" :show-text="false"
                    :color="row.completion_rate >= 90 ? '#67c23a' : row.completion_rate >= 70 ? '#e6a23c' : '#f56c6c'" />
                  <span>{{ row.completion_rate }}%</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="质量趋势" name="quality">
        <el-card shadow="never" v-loading="qtLoading">
          <template #header>
            <div class="report-header">
              <span>近30天不良率趋势</span>
            </div>
          </template>
          <el-table :data="qualityData" size="small" max-height="480">
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="total_inspected" label="检验总数" />
            <el-table-column label="不良率">
              <template #default="{ row }">
                <div style="display:flex;align-items:center;gap:8px">
                  <el-progress :percentage="Math.min(row.defect_rate, 100)" :stroke-width="16" :show-text="false"
                    :color="row.defect_rate <= 5 ? '#67c23a' : row.defect_rate <= 15 ? '#e6a23c' : '#f56c6c'" />
                  <span>{{ row.defect_rate }}%</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
/**
 * 生产报表页面组件
 * 包含三个标签页：生产日报、工单完成率趋势、质量趋势
 * 各标签页按需加载数据，避免一次性请求所有报表
 */
import { ref, computed, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { dashboardAPI } from '@/api'

// ── 状态与标签页数据 ──
const activeTab = ref('daily')     // 当前激活的标签页
const loading = ref(false)         // 生产日报加载状态
const crLoading = ref(false)       // 完成率数据加载状态
const qtLoading = ref(false)       // 质量趋势数据加载状态
const dailyData = ref({})          // 生产日报数据
const completionData = ref([])     // 工单完成率趋势列表
const qualityData = ref([])        // 质量趋势列表

// ── 计算属性 ──
// 将生产日报原始数据转换为卡片展示格式
const dailyCards = computed(() => {
  const d = dailyData.value
  return [
    { label: '计划产量', value: d.plan_qty ?? '-' },
    { label: '实际产量', value: d.actual_qty ?? '-' },
    { label: '合格数', value: d.qualified_qty ?? '-' },
    { label: '不合格数', value: d.defect_qty ?? '-' },
    { label: '开工工单', value: d.started_wo ?? '-' },
    { label: '完工工单', value: d.completed_wo ?? '-' },
    { label: '设备稼动率', value: d.utilization_rate != null ? d.utilization_rate + '%' : '-' },
    { label: '在线工人数', value: d.online_workers ?? '-' },
  ]
})

// ── 数据获取 ──
// 获取今日生产日报数据
async function fetchDaily() {
  loading.value = true
  try {
    const res = await dashboardAPI.prodDaily()
    dailyData.value = res.data || res || {}
  } finally { loading.value = false }
}

// 获取近30天工单完成率趋势
async function fetchCompletionRate() {
  crLoading.value = true
  try {
    const res = await dashboardAPI.completionRate()
    completionData.value = res.data || res || []
  } finally { crLoading.value = false }
}

// 获取近30天质量趋势（不良率）
async function fetchQualityTrend() {
  qtLoading.value = true
  try {
    const res = await dashboardAPI.qualityTrend()
    qualityData.value = res.data || res || []
  } finally { qtLoading.value = false }
}

// ── 标签页切换 ──
// 切换标签时按需加载对应数据（仅首次切换时请求）
function onTabChange(tab) {
  if (tab === 'completion' && completionData.value.length === 0) fetchCompletionRate()
  if (tab === 'quality' && qualityData.value.length === 0) fetchQualityTrend()
}

onMounted(() => fetchDaily())
</script>

<style scoped>
.report-header {
  display: flex; justify-content: space-between; align-items: center;
}

.metric-card {
  background: #f5f7fa; border-radius: 8px; padding: 16px;
  text-align: center; margin-bottom: 12px;
}
.metric-card__label { font-size: 13px; color: #909399; margin-bottom: 8px; }
.metric-card__value { font-size: 22px; font-weight: 700; color: #303133; }
</style>
