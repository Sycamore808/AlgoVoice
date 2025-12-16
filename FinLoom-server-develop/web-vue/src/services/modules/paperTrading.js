/**
 * 模拟交易API服务
 */
import apiClient from '../client'

export const paperTradingApi = {
  // ========== 账户管理 ==========
  
  /**
   * 创建模拟交易账户
   */
  createAccount: (accountId, initialCash = 1000000) => 
    apiClient.post('/paper-trading/accounts', {
      account_id: accountId,
      initial_cash: initialCash
    }),

  /**
   * 获取账户信息
   */
  getAccount: (accountId) => 
    apiClient.get(`/paper-trading/accounts/${accountId}`),

  // ========== 订单管理 ==========
  
  /**
   * 提交订单
   */
  submitOrder: (orderData) => 
    apiClient.post('/paper-trading/orders', orderData),

  /**
   * 获取账户订单列表
   */
  getOrders: (accountId) => 
    apiClient.get(`/paper-trading/orders/${accountId}`),

  // ========== 策略管理 ==========
  
  /**
   * 创建策略
   */
  createStrategy: (strategyData) => 
    apiClient.post('/paper-trading/strategies', strategyData),

  /**
   * 获取用户策略列表
   */
  getUserStrategies: (userId) => 
    apiClient.get(`/paper-trading/strategies/user/${userId}`),

  /**
   * 获取策略详情
   */
  getStrategy: (strategyId) => 
    apiClient.get(`/paper-trading/strategies/${strategyId}`),

  /**
   * 激活/停用策略
   */
  activateStrategy: (strategyId, isActive) => 
    apiClient.post('/paper-trading/strategies/activate', {
      strategy_id: strategyId,
      is_active: isActive
    }),

  /**
   * 获取策略表现
   */
  getStrategyPerformance: (strategyId) => 
    apiClient.get(`/paper-trading/strategies/${strategyId}/performance`)
}

