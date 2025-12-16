<template>
  <div class="my-strategies-view">
    <div class="page-header">
      <h1 class="page-title">
        <v-icon icon="mdi-brain" class="mr-2"></v-icon>
        我的策略
      </h1>
      <p class="page-subtitle">管理和查看您的量化交易策略</p>
    </div>

    <!-- 加载中 -->
    <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>

    <!-- 策略列表 -->
    <v-row v-else>
      <v-col v-if="strategies.length === 0" cols="12">
        <v-alert type="info" variant="tonal">
          <v-alert-title>暂无策略</v-alert-title>
          <div>您还没有创建任何策略。请联系管理员或使用平台功能创建策略。</div>
        </v-alert>
      </v-col>

      <v-col v-for="strategy in strategies" :key="strategy.strategy_id" cols="12" md="6" lg="4">
        <v-card class="strategy-card" :class="{ 'active-strategy': strategy.is_active }">
          <!-- 状态指示器 -->
          <div class="strategy-status-indicator" :class="strategy.is_active ? 'active' : 'inactive'"></div>

          <v-card-title class="d-flex align-center justify-space-between">
            <span class="text-truncate">{{ strategy.strategy_name }}</span>
            <v-chip :color="strategy.is_active ? 'success' : 'default'" size="small">
              {{ strategy.is_active ? '运行中' : '已停止' }}
            </v-chip>
          </v-card-title>

          <v-card-subtitle class="text-caption text-grey">
            ID: {{ strategy.strategy_id }}
          </v-card-subtitle>

          <v-card-text>
            <p class="strategy-description text-body-2 mb-4">
              {{ strategy.description || '暂无描述' }}
            </p>

            <!-- 策略统计 -->
            <v-row class="strategy-stats" dense>
              <v-col cols="6">
                <div class="stat-item">
                  <v-icon size="small" class="mr-1">mdi-play-circle</v-icon>
                  <span class="text-caption">执行次数</span>
                  <div class="stat-value">{{ strategy.total_runs || 0 }}</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="stat-item">
                  <v-icon size="small" class="mr-1" :color="profitColor(strategy.total_profit)">mdi-currency-cny</v-icon>
                  <span class="text-caption">总盈亏</span>
                  <div class="stat-value" :class="profitClass(strategy.total_profit)">
                    {{ formatProfit(strategy.total_profit) }}
                  </div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="stat-item">
                  <v-icon size="small" class="mr-1">mdi-chart-line</v-icon>
                  <span class="text-caption">胜率</span>
                  <div class="stat-value">{{ formatPercent(strategy.win_rate) }}</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="stat-item">
                  <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                  <span class="text-caption">最后运行</span>
                  <div class="stat-value text-caption">{{ formatDate(strategy.last_run_time) }}</div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions>
            <v-btn 
              :color="strategy.is_active ? 'warning' : 'success'"
              variant="tonal"
              size="small"
              @click="toggleStrategy(strategy)"
            >
              <v-icon start>{{ strategy.is_active ? 'mdi-pause' : 'mdi-play' }}</v-icon>
              {{ strategy.is_active ? '停止' : '启动' }}
            </v-btn>

            <v-btn
              color="primary"
              variant="tonal"
              size="small"
              @click="viewPerformance(strategy)"
            >
              <v-icon start>mdi-chart-box</v-icon>
              查看详情
            </v-btn>

            <v-spacer></v-spacer>

            <v-btn
              icon
              size="small"
              variant="text"
              @click="refreshStrategy(strategy)"
            >
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- 性能详情对话框 -->
    <v-dialog v-model="performanceDialog" max-width="800">
      <v-card v-if="selectedStrategy">
        <v-card-title class="d-flex align-center justify-space-between">
          <span>{{ selectedStrategy.strategy_name }} - 性能详情</span>
          <v-btn icon="mdi-close" variant="text" @click="performanceDialog = false"></v-btn>
        </v-card-title>

        <v-card-text>
          <v-progress-linear v-if="loadingPerformance" indeterminate></v-progress-linear>

          <div v-else-if="performance">
            <!-- 汇总统计 -->
            <v-row class="mb-4">
              <v-col cols="3">
                <v-card variant="tonal">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ performance.total_runs }}</div>
                    <div class="text-caption text-grey">总执行次数</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="3">
                <v-card variant="tonal">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ performance.successful_runs }}</div>
                    <div class="text-caption text-grey">成功次数</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="3">
                <v-card variant="tonal">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ formatPercent(performance.success_rate) }}</div>
                    <div class="text-caption text-grey">成功率</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="3">
                <v-card variant="tonal">
                  <v-card-text class="text-center">
                    <div class="text-h4" :class="profitClass(performance.total_profit)">
                      {{ formatProfit(performance.total_profit) }}
                    </div>
                    <div class="text-caption text-grey">总盈亏</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- 最近执行记录 -->
            <v-card variant="outlined">
              <v-card-title class="text-subtitle-1">最近执行记录</v-card-title>
              <v-card-text>
                <v-list dense>
                  <v-list-item 
                    v-for="(exec, index) in performance.recent_executions" 
                    :key="index"
                    :class="exec.status === 'success' ? 'success-exec' : 'failed-exec'"
                  >
                    <template v-slot:prepend>
                      <v-icon :color="exec.status === 'success' ? 'success' : 'error'">
                        {{ exec.status === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                      </v-icon>
                    </template>
                    <v-list-item-title>{{ formatDateTime(exec.execution_time) }}</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ exec.status === 'success' ? '执行成功' : exec.error_message || '执行失败' }}
                      <span v-if="exec.status === 'success'" class="ml-2" :class="profitClass(exec.profit_loss)">
                        {{ formatProfit(exec.profit_loss) }}
                      </span>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </div>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="performanceDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const loading = ref(true)
const strategies = ref([])
const selectedStrategy = ref(null)
const performanceDialog = ref(false)
const loadingPerformance = ref(false)
const performance = ref(null)

// 加载策略列表
async function loadStrategies() {
  try {
    loading.value = true
    
    // 确保用户信息已加载
    if (!userStore.username) {
      await userStore.fetchUserInfo()
    }
    
    console.log('Loading strategies for user:', userStore.username)
    const response = await api.paperTrading.getUserStrategies(userStore.username)
    console.log('Strategies response:', response)
    
    if (response.success) {
      strategies.value = response.data
      console.log('Loaded strategies:', strategies.value)
    } else {
      console.error('Failed to load strategies: response not successful')
    }
  } catch (error) {
    console.error('Failed to load strategies:', error)
    console.error('Error details:', error.response?.data || error.message)
  } finally {
    loading.value = false
  }
}

// 切换策略状态
async function toggleStrategy(strategy) {
  try {
    const newStatus = !strategy.is_active
    await api.paperTrading.activateStrategy(strategy.strategy_id, newStatus)
    strategy.is_active = newStatus
  } catch (error) {
    console.error('Failed to toggle strategy:', error)
  }
}

// 查看策略性能
async function viewPerformance(strategy) {
  selectedStrategy.value = strategy
  performanceDialog.value = true
  loadingPerformance.value = true
  performance.value = null

  try {
    const response = await api.paperTrading.getStrategyPerformance(strategy.strategy_id)
    if (response.success) {
      performance.value = response.data
    }
  } catch (error) {
    console.error('Failed to load performance:', error)
  } finally {
    loadingPerformance.value = false
  }
}

// 刷新单个策略
async function refreshStrategy(strategy) {
  try {
    const response = await api.paperTrading.getStrategy(strategy.strategy_id)
    if (response.success) {
      Object.assign(strategy, response.data)
    }
  } catch (error) {
    console.error('Failed to refresh strategy:', error)
  }
}

// 格式化函数
function formatProfit(value) {
  if (!value) return '¥0.00'
  return value >= 0 ? `+¥${value.toFixed(2)}` : `-¥${Math.abs(value).toFixed(2)}`
}

function profitClass(value) {
  if (!value) return ''
  return value >= 0 ? 'text-success' : 'text-error'
}

function profitColor(value) {
  if (!value) return 'grey'
  return value >= 0 ? 'success' : 'error'
}

function formatPercent(value) {
  if (value === null || value === undefined) return '0%'
  return `${value.toFixed(1)}%`
}

function formatDate(dateStr) {
  if (!dateStr) return '未运行'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const hours = Math.floor(diff / 3600000)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadStrategies()
})
</script>

<style scoped>
.my-strategies-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #666;
  margin: 0;
}

.strategy-card {
  position: relative;
  height: 100%;
  transition: all 0.3s ease;
}

.strategy-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.active-strategy {
  border-left: 4px solid #4caf50;
}

.strategy-status-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.strategy-status-indicator.active {
  background-color: #4caf50;
  animation: pulse 2s infinite;
}

.strategy-status-indicator.inactive {
  background-color: #9e9e9e;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.strategy-description {
  min-height: 40px;
  color: #666;
}

.strategy-stats {
  margin-top: 12px;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 8px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  margin-top: 4px;
}

.text-success {
  color: #4caf50;
}

.text-error {
  color: #f44336;
}

.success-exec {
  background-color: rgba(76, 175, 80, 0.05);
}

.failed-exec {
  background-color: rgba(244, 67, 54, 0.05);
}
</style>

