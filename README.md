# AlgoVoice - 智能量化投资引擎

> 基于AI技术的智能量化投资系统，为投资者提供便捷、低成本、智能化的量化交易服务。支持自然语言交互，自动生成个性化投资策略。

---

## ⚠️ 重要声明

**本项目采用专有许可证，仅供学习和技术交流使用。**

- ❌ **禁止商业使用**
- ❌ **禁止未经授权的复制、修改和分发**
- ❌ **禁止部署到生产环境**
- ✅ **如需合作或商业授权，请通过 [Issues](https://github.com/Sycamore808/AlgoVoice/issues) 联系**

查看完整许可证：[LICENSE](LICENSE)

---

## 🚀 核心功能

- **🤖 自然语言交互**：用日常语言描述投资需求，AI自动生成策略
- **📊 智能因子挖掘**：基于遗传编程自动筛选有效因子
- **⚡ 实时回测验证**：支持Baostock数据源，快速验证策略
- **🛡️ 动态风险控制**：自适应仓位管理，控制回撤
- **💰 低门槛普惠**：降低量化投资门槛，让更多人享受专业服务

## 🏗️ 项目结构

```
AlgoVoice/
├── AlgoVoice-server-main/       # 稳定版本
└── AlgoVoice-server-develop/    # 开发版本（包含最新功能）
    ├── backtest_baostock/       # 回测系统
    ├── web-vue/                 # Web前端
    └── module_XX/               # 11个核心模块
```

## 🚀 快速开始

### 方式1：使用稳定版本

```bash
cd AlgoVoice-server-main
pip install -r requirements.txt
python main.py
```

### 方式2：使用开发版本（推荐）

#### Windows用户
```bash
cd AlgoVoice-server-develop
首次安装.bat
启动.bat
```

#### Linux/Mac用户
```bash
cd AlgoVoice-server-develop
pip install -r requirements.txt
python main.py
```

### 回测系统

```bash
cd AlgoVoice-server-develop/backtest_baostock
快速测试.bat
```

## 📚 技术栈

- **后端**：Python 3.8+
- **前端**：Vue 3 + Vuetify
- **数据源**：Baostock / AkShare
- **回测引擎**：自研高性能回测系统

## 📖 详细文档

- [系统架构](AlgoVoice-server-develop/docs/)
- [回测系统使用](AlgoVoice-server-develop/backtest_baostock/README.txt)
- [Web前端开发](AlgoVoice-server-develop/web-vue/README.md)

## 📄 许可证

MIT License

## ⚠️ 免责声明

本系统仅供学术研究和技术交流使用。投资有风险，使用需谨慎。

---

⭐ 如果觉得有帮助，请给个Star支持！
