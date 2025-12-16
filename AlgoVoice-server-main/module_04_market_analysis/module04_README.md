# Module 04 - 市场分析模块 (Enhanced with Trading Agents)

## 概述

市场分析模块是 AlgoVoice 量化交易系统的核心智能分析组件，集成了先进的多智能体交易分析框架，使用真实的中国A股数据进行深度市场分析。该模块已完全整合原Trading Agents功能，提供更强大、更智能的市场分析能力。

## 🚀 主要特性

### 1. 多智能体分析系统
- **情感分析师**: 集成FIN-R1模型和新闻情感分析
- **基本面分析师**: 财务数据和宏观经济分析  
- **技术分析师**: 技术指标和图表形态识别
- **风险管理师**: 风险评估和投资建议
- **智能体协调器**: 多轮辩论和共识构建

### 2. 增强的情感分析
- **FIN-R1模型集成**: 专业金融文本情感分析
- **新闻情感分析**: 实时新闻和社交媒体情绪追踪
- **市场情感聚合**: 多源情感数据综合分析
- **情感趋势追踪**: 历史情感变化趋势分析

### 3. 异常检测与预警
- **价格异常检测**: 基于统计和机器学习的价格异常识别
- **成交量异常**: 交易量异常变化检测
- **技术形态异常**: 图表形态突破和反转检测
- **多维度异常**: 综合多个维度的异常评分

## 📊 数据集成

### Module 1 数据源集成
- **实时行情数据**: AkshareDataCollector
- **宏观经济数据**: 中国GDP、CPI、PMI等指标
- **新闻数据**: 新闻联播、财经新闻、个股新闻
- **基本面数据**: 财务报表、财务指标、分红数据

### Module 2 技术指标集成
- **技术指标计算**: 移动平均、RSI、MACD、布林带
- **特征工程**: 时间序列特征、图网络特征
- **因子分析**: 多因子模型和因子发现

### 专用数据库存储
- **SQLite数据库**: `/data/module04_market_analysis.db`
- **分析结果存储**: 智能体分析历史和共识结果
- **情感分析记录**: 情感分析历史和趋势数据
- **异常检测记录**: 异常事件和预警历史

## 🔧 安装和配置

### 环境要求
```bash
# 激活conda环境
conda activate study

# 确保必要的依赖包已安装
pip install fastapi uvicorn pandas numpy scipy scikit-learn
pip install transformers torch  # 用于FIN-R1模型
```

### 数据库初始化
数据库会在首次使用时自动创建，位置：
```
/Users/victor/Desktop/25fininnov/AlgoVoice-server/data/module04_market_analysis.db
```

## 🚀 快速开始

### 1. 基础使用示例

```python
import asyncio
from module_04_market_analysis.sentiment_analysis.fin_r1_sentiment import get_sentiment_analyzer

async def basic_example():
    # 基础情感分析
    analyzer = get_sentiment_analyzer()
    symbols = ["000001", "600036", "000858"]  # 平安银行、招商银行、五粮液
    
    # 分析股票情感
    result = await analyzer.analyze_stock_sentiment(symbols)
    print(f"整体情感分数: {result['overall_sentiment']['sentiment_score']:.3f}")
    
    # 分析市场情感
    market_result = await analyzer.analyze_market_sentiment()
    print(f"市场情感分数: {market_result['overall_sentiment']:.3f}")

# 运行示例
asyncio.run(basic_example())
```

### 2. 增强情感分析（集成基本面）

```python
from module_04_market_analysis.sentiment_analysis.enhanced_news_sentiment import EnhancedNewsSentimentAnalyzer

async def enhanced_sentiment_example():
    # 增强情感分析（新闻+基本面）
    enhanced_analyzer = EnhancedNewsSentimentAnalyzer()
    symbols = ["000001", "600036"]
    
    # 综合分析
    result = await enhanced_analyzer.analyze_comprehensive_sentiment(symbols)
    
    for symbol, analysis in result['individual_results'].items():
        print(f"{symbol}:")
        print(f"  最终情感: {analysis['final_sentiment_label']}")
        print(f"  置信度: {analysis['final_confidence']:.2f}")
        print(f"  投资建议: {analysis['recommendation']}")

asyncio.run(enhanced_sentiment_example())
```

## 📡 REST API 接口

### 启动API服务器

```python
from fastapi import FastAPI
from module_04_market_analysis.api.market_analysis_api import router

app = FastAPI(title="Market Analysis API")
app.include_router(router)

# 运行服务器
# uvicorn main:app --host 0.0.0.0 --port 8000
```

### API 端点

#### 1. 情感分析端点

**POST /api/v1/market/sentiment/analyze**
```bash
curl -X POST "http://localhost:8000/api/v1/market/sentiment/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "symbols": ["000001", "600036"],
       "include_fundamentals": true
     }'
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "overall_sentiment": {
      "sentiment_score": 0.234,
      "sentiment_label": "positive",
      "confidence": 0.78
    },
    "individual_stocks": {
      "000001": {
        "sentiment_score": 0.156,
        "sentiment_label": "positive",
        "confidence": 0.82,
        "news_count": 15
      }
    }
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

#### 2. 市场情感端点

**GET /api/v1/market/sentiment/market**
```bash
curl "http://localhost:8000/api/v1/market/sentiment/market"
```

#### 3. 股票数据端点

**GET /api/v1/market/data/stocks/{symbol}**
```bash
curl "http://localhost:8000/api/v1/market/data/stocks/000001?period=30"
```

#### 4. 实时数据端点

**GET /api/v1/market/data/realtime**
```bash
curl "http://localhost:8000/api/v1/market/data/realtime?symbols=000001&symbols=600036"
```

#### 5. 健康检查端点

**GET /api/v1/market/health**
```bash
curl "http://localhost:8000/api/v1/market/health"
```

**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "services": {
    "data_collector": true,
    "sentiment_analyzer": true,
    "enhanced_sentiment": true,
    "database": true
  }
}
```

## 🔧 模块间调用方法

### 从其他模块调用 Module 4

#### 1. Python程序调用
```python
# 在其他模块中导入和使用
from module_04_market_analysis.sentiment_analysis.fin_r1_sentiment import (
    get_sentiment_analyzer,
    analyze_symbol_sentiment,
    analyze_market_sentiment
)

# 异步调用
import asyncio

async def analyze_market():
    # 分析特定股票情感
    result = await analyze_symbol_sentiment(["000001", "600036"])
    return result

# 同步调用包装
def sync_analyze_market():
    return asyncio.run(analyze_market())
```

#### 2. 从 Module 9 (回测) 调用
```python
# 在回测模块中获取市场情感数据
from module_04_market_analysis.sentiment_analysis.fin_r1_sentiment import get_sentiment_analyzer

class BacktestEngine:
    def __init__(self):
        self.sentiment_analyzer = get_sentiment_analyzer()
    
    async def get_market_sentiment_for_date(self, date, symbols):
        # 获取指定日期的市场情感
        sentiment_data = await self.sentiment_analyzer.analyze_stock_sentiment(symbols)
        return sentiment_data
```

### 前后端API交互

#### 1. 前端JavaScript调用示例
```javascript
// 前端调用市场分析API
class MarketAnalysisClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    // 分析股票情感
    async analyzeStockSentiment(symbols, includeFundamentals = true) {
        const response = await fetch(`${this.baseUrl}/api/v1/market/sentiment/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbols: symbols,
                include_fundamentals: includeFundamentals
            })
        });
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    // 获取市场情感
    async getMarketSentiment() {
        const response = await fetch(`${this.baseUrl}/api/v1/market/sentiment/market`);
        return await response.json();
    }
}

// 使用示例
const client = new MarketAnalysisClient();

// 分析情感
client.analyzeStockSentiment(['000001', '600036'])
    .then(result => {
        console.log('情感分析结果:', result);
        updateSentimentDisplay(result.data);
    })
    .catch(error => {
        console.error('分析失败:', error);
    });
```

#### 2. React组件示例
```jsx
import React, { useState, useEffect } from 'react';

const MarketAnalysisComponent = () => {
    const [sentimentData, setSentimentData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [symbols] = useState(['000001', '600036', '000858']);
    
    const analyzeSentiment = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/market/sentiment/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbols: symbols,
                    include_fundamentals: true
                })
            });
            
            const result = await response.json();
            setSentimentData(result.data);
        } catch (error) {
            console.error('情感分析失败:', error);
        } finally {
            setLoading(false);
        }
    };
    
    useEffect(() => {
        analyzeSentiment();
    }, []);
    
    return (
        <div className="market-analysis">
            <h2>市场情感分析</h2>
            
            {loading && <div>正在分析中...</div>}
            
            {sentimentData && (
                <div>
                    <div className="overall-sentiment">
                        <h3>整体情感</h3>
                        <p>分数: {sentimentData.overall_sentiment.sentiment_score.toFixed(3)}</p>
                        <p>标签: {sentimentData.overall_sentiment.sentiment_label}</p>
                        <p>置信度: {sentimentData.overall_sentiment.confidence.toFixed(2)}</p>
                    </div>
                    
                    <div className="individual-stocks">
                        <h3>个股情感</h3>
                        {Object.entries(sentimentData.individual_stocks).map(([symbol, data]) => (
                            <div key={symbol} className="stock-sentiment">
                                <h4>{symbol}</h4>
                                <p>情感: {data.sentiment_label}</p>
                                <p>分数: {data.sentiment_score.toFixed(3)}</p>
                                <p>置信度: {data.confidence.toFixed(2)}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            <button onClick={analyzeSentiment} disabled={loading}>
                刷新分析
            </button>
        </div>
    );
};

export default MarketAnalysisComponent;
```

## 🧪 测试和验证

### 运行测试
```bash
# 激活conda环境
conda activate study

# 进入项目目录
cd /Users/victor/Desktop/25fininnov/AlgoVoice-server

# 运行Module 4测试
python tests/module04_market_analysis_test.py
```

### 测试覆盖内容
1. **模块导入测试**: 验证所有组件正确导入
2. **真实数据采集**: 测试数据源集成
3. **情感分析功能**: 测试FIN-R1和增强情感分析
4. **异常检测**: 测试价格、成交量和多维异常检测
5. **相关性分析**: 测试股票相关性计算
6. **市场状态检测**: 测试HMM和其他状态检测方法
7. **数据库操作**: 测试SQLite存储和检索
8. **API结构**: 验证REST API端点
9. **集成工作流**: 端到端数据流测试

### 预期测试结果
```
Module 04 Market Analysis - Comprehensive Test Suite
============================================================
Testing market analysis with real A-share data
Database: /Users/victor/Desktop/25fininnov/AlgoVoice-server/data/module04_market_analysis.db
============================================================

Test 1: Module Imports Test
✓ Sentiment analysis imports successful
✓ Anomaly detection imports successful
✓ Correlation analysis imports successful
✓ Regime detection imports successful
✓ Database imports successful
✓ API imports successful

Test 2: Real Data Integration Test
✓ 000001: 平安银行 - 银行
✓ 600036: 招商银行 - 银行
✓ 000858: 五粮液 - 白酒
✓ Data integration successful

🎉 ALL TESTS PASSED! Module 04 is ready for use.
```

## ❓ 常见问题

### 1. 导入错误
```bash
ImportError: No module named 'module_01_data_pipeline'
```
**解决方案**: 确保在正确的conda环境中运行
```bash
conda activate study
```

### 2. 数据库连接错误
```bash
sqlite3.OperationalError: database is locked
```
**解决方案**: 检查数据库文件权限，重启服务

### 3. API连接问题
```bash
ConnectionError: Failed to connect to API
```
**解决方案**: 确保主服务器正在运行
```bash
python main.py
```

### 4. FIN-R1模型问题
```bash
Model not found or failed to load
```
**解决方案**: 检查模型路径或使用关键词分析后备方案

### 调试模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
from module_04_market_analysis.sentiment_analysis.fin_r1_sentiment import FINR1SentimentAnalyzer
analyzer = FINR1SentimentAnalyzer()
```