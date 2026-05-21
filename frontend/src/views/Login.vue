<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="36" color="#409EFF"><Setting /></el-icon>
        <h1>生产管理系统</h1>
        <p>Production Management System</p>
      </div>
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
import { User, Lock } from '@element-plus/icons-vue'
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
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
.login-card {
  width: 400px; padding: 40px;
  background: rgba(255,255,255,0.95); border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.login-header { text-align: center; margin-bottom: 32px; }
.login-header h1 { margin: 8px 0 4px; font-size: 22px; color: #1a1a2e; }
.login-header p { font-size: 12px; color: #909399; }
</style>
