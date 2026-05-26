<template>
  <div class="login-container">
    <div class="login-left">
      <!-- 装饰圆 -->
      <div class="deco deco-1"></div>
      <div class="deco deco-2"></div>
      <div class="deco deco-3"></div>

      <div class="login-brand">
        <div class="brand-icon">
          <el-icon :size="36"><Setting /></el-icon>
        </div>
        <h1>生产管理系统</h1>
        <p>Production Management System</p>
      </div>

      <div class="login-features">
        <div class="feature-item">
          <div class="feature-icon"><el-icon :size="18"><Tickets /></el-icon></div>
          <div>
            <div class="feature-title">订单驱动</div>
            <div class="feature-desc">从客户订单到工单派发，全流程数字化管理</div>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon"><el-icon :size="18"><Monitor /></el-icon></div>
          <div>
            <div class="feature-title">实时监控</div>
            <div class="feature-desc">生产进度、设备状态、工时报工一目了然</div>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon"><el-icon :size="18"><CircleCheck /></el-icon></div>
          <div>
            <div class="feature-title">质量管控</div>
            <div class="feature-desc">检验标准统一管理，不良品全程可追溯</div>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon"><el-icon :size="18"><Box /></el-icon></div>
          <div>
            <div class="feature-title">库存可视</div>
            <div class="feature-desc">出入库实时更新，多仓库库存一表查询</div>
          </div>
        </div>
      </div>

      <div class="login-footer">
        <span>V1.0</span>
      </div>
    </div>

    <div class="login-right">
      <div class="login-card">
        <h2>欢迎登录</h2>
        <p class="login-subtitle">请输入您的账号信息</p>
        <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password size="large" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">
              登 录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <p class="right-footer">&copy; 2026 生产管理系统</p>
    </div>
  </div>
</template>

<script setup>
/**
 * 登录页面组件
 * 包含用户名/密码登录表单，支持表单校验和回车登录
 * 登录成功后将 token 存入 authStore 并跳转至仪表盘
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Tickets, Monitor, CircleCheck, Box } from '@element-plus/icons-vue'
import { authAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'

// ── 状态与表单数据 ──
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const form = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// ── 登录处理 ──
// 调用登录接口，成功后存储 token 并跳转到仪表盘
async function handleLogin() {
  loading.value = true
  try {
    const res = await authAPI.login(form.value)
    if (res.code === 200) {
      authStore.login(res.data)
      ElMessage.success('登录成功')
      router.push('/dashboard')
    }
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
}

/* ===== 左侧品牌区 ===== */
.login-left {
  flex: 1;
  background: #0F172A;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #fff;
  position: relative;
  overflow: hidden;
  transition: flex .5s cubic-bezier(.4,0,.2,1);
}
.login-left:hover {
  flex: 1.15;
}
.login-left:hover ~ .login-right {
  flex: 0.85;
}

/* 装饰圆 */
.deco {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(96,165,250,.12);
}
.deco-1 { width: 300px; height: 300px; top: -80px; right: -80px; }
.deco-2 { width: 200px; height: 200px; bottom: -60px; left: -60px; }
.deco-3 { width: 120px; height: 120px; top: 40%; right: 10%; border-color: rgba(96,165,250,.08); }

.login-brand {
  text-align: center;
  margin-bottom: 48px;
}
.brand-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: rgba(96,165,250,.15);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: #60A5FA;
  transition: transform .4s cubic-bezier(.4,0,.2,1);
}
.login-left:hover .brand-icon {
  transform: scale(1.08);
}
.login-brand h1 {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: 2px;
}
.login-brand p {
  font-size: 13px;
  color: #94A3B8;
  margin: 0;
  letter-spacing: 1px;
}

/* 功能亮点 */
.login-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  max-width: 360px;
}
.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.06);
  transition: background .2s;
}
.feature-item:hover { background: rgba(255,255,255,.08); }
.feature-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(96,165,250,.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #60A5FA;
  flex-shrink: 0;
}
.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: #E2E8F0;
  margin-bottom: 4px;
}
.feature-desc {
  font-size: 12px;
  color: #94A3B8;
  line-height: 1.5;
}

/* 底部版本 */
.login-footer {
  position: absolute;
  bottom: 24px;
  font-size: 12px;
  color: #475569;
}

/* ===== 右侧登录区 ===== */
.login-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  transition: flex .5s cubic-bezier(.4,0,.2,1);
}
.login-right:hover {
  flex: 1.15;
}
.login-container:has(.login-right:hover) .login-left {
  flex: 0.85;
}
.login-card {
  width: 400px;
  padding: 44px 40px;
  background: var(--bg-white);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  transition: transform .4s cubic-bezier(.4,0,.2,1), box-shadow .4s;
}
.login-container:has(.login-right:hover) .login-card {
  transform: scale(1.02);
  box-shadow: 0 20px 40px rgba(0,0,0,.12);
}
.login-card h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 8px;
}
.login-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0 0 28px;
}
.right-footer {
  margin-top: 24px;
  font-size: 12px;
  color: var(--text-muted);
}
</style>
