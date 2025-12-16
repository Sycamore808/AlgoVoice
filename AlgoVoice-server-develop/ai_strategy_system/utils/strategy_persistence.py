#!/usr/bin/env python3
"""策略持久化管理器 - 保存和加载策略"""

from __future__ import annotations

import inspect
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch

from common.logging_system import setup_logger

LOGGER = setup_logger("strategy_persistence")


class StrategyPersistence:
    """策略持久化管理器

    功能:
    1. 保存策略代码、模型、配置到文件系统
    2. 加载已保存的策略
    3. 列出所有已保存的策略
    4. 策略版本管理
    """

    def __init__(self, base_dir: str = "ai_strategy_system/generated_strategies"):
        """初始化持久化管理器

        Args:
            base_dir: 策略保存的根目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"📁 策略持久化目录: {self.base_dir.absolute()}")

    def _format_params(self, params: Dict[str, Any]) -> str:
        """格式化参数字典为可读字符串"""
        lines = []
        for key, value in params.items():
            if isinstance(value, dict):
                lines.append(f"  {key}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"    - {sub_key}: {sub_value}")
            else:
                lines.append(f"  - {key}: {value}")
        return "\n".join(lines)

    def save_strategy(
        self,
        strategy_code: Any,  # StrategyCode对象
        trained_model: Optional[Any] = None,
        config: Optional[Dict] = None,
        backtest_result: Optional[Any] = None,
        user_requirement: Optional[str] = None,
    ) -> str:
        """保存完整策略

        Args:
            strategy_code: 策略代码对象
            trained_model: 训练好的模型
            config: 策略配置字典
            backtest_result: 回测结果对象
            user_requirement: 用户原始需求

        Returns:
            strategy_id: 策略唯一标识
        """
        # 生成策略ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_type = config.get("model_type", "unknown") if config else "unknown"
        strategy_id = f"strategy_{timestamp}_{model_type}"

        strategy_dir = self.base_dir / strategy_id
        strategy_dir.mkdir(exist_ok=True)

        LOGGER.info(f"💾 开始保存策略: {strategy_id}")

        # 1. 保存策略代码
        try:
            code_file = strategy_dir / "strategy.py"

            # 尝试保存真实的Python源代码
            if hasattr(strategy_code, "strategy_function"):
                try:
                    # 获取函数源代码
                    func_source = inspect.getsource(strategy_code.strategy_function)

                    # 构建完整的可执行Python文件
                    full_code = f'''#!/usr/bin/env python3
"""
{getattr(strategy_code, "strategy_name", "量化策略")}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
版本: {getattr(strategy_code, "version", "1.0.0")}

策略描述:
{getattr(strategy_code, "description", "智能量化交易策略")}

策略参数:
{self._format_params(getattr(strategy_code, "parameters", {}))}
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from common.data_structures import Signal

# ==================== 策略函数 ====================

{func_source}

# ==================== 策略元信息 ====================

STRATEGY_INFO = {{
    "name": "{getattr(strategy_code, "strategy_name", "未命名策略")}",
    "version": "{getattr(strategy_code, "version", "1.0.0")}",
    "description": "{getattr(strategy_code, "description", "")}",
    "parameters": {getattr(strategy_code, "parameters", {})},
    "created_at": "{getattr(strategy_code, "created_at", datetime.now()).isoformat()}"
}}
'''
                    with open(code_file, "w", encoding="utf-8") as f:
                        f.write(full_code)
                    LOGGER.info(
                        f"  ✅ 策略源代码已保存: {code_file.name} ({len(full_code)} bytes)"
                    )
                except (OSError, TypeError) as e:
                    # 如果获取源代码失败，保存说明文档
                    LOGGER.warning(f"  ⚠️  无法获取函数源代码: {e}，保存说明文档")
                    strategy_code_str = getattr(
                        strategy_code, "code", str(strategy_code)
                    )
                    with open(code_file, "w", encoding="utf-8") as f:
                        f.write(strategy_code_str)
            else:
                # 如果没有strategy_function属性，保存code字符串
                strategy_code_str = getattr(strategy_code, "code", str(strategy_code))
                with open(code_file, "w", encoding="utf-8") as f:
                    f.write(strategy_code_str)
                LOGGER.info(f"  ✅ 策略描述已保存: {code_file.name}")
        except Exception as e:
            LOGGER.warning(f"  ⚠️  保存策略代码失败: {e}")

        # 2. 保存训练模型
        if trained_model is not None:
            try:
                model_file = strategy_dir / "model.pth"
                if hasattr(trained_model, "state_dict"):
                    torch.save(trained_model.state_dict(), model_file)
                    LOGGER.info(f"  ✅ 模型已保存: {model_file.name}")
                elif hasattr(trained_model, "save"):
                    trained_model.save(str(model_file))
                    LOGGER.info(f"  ✅ 模型已保存: {model_file.name}")
                else:
                    LOGGER.warning(f"  ⚠️  模型类型不支持保存: {type(trained_model)}")
            except Exception as e:
                LOGGER.warning(f"  ⚠️  保存模型失败: {e}")

        # 3. 保存策略配置
        try:
            config_data = config or {}

            # 添加元信息
            config_data.update(
                {
                    "strategy_id": strategy_id,
                    "created_at": datetime.now().isoformat(),
                    "strategy_name": getattr(strategy_code, "strategy_name", "Unknown"),
                    "version": getattr(strategy_code, "version", "1.0.0"),
                    "description": getattr(strategy_code, "description", ""),
                }
            )

            # 添加用户需求
            if user_requirement:
                config_data["user_requirement"] = user_requirement

            # 添加策略参数
            if hasattr(strategy_code, "parameters"):
                config_data["parameters"] = strategy_code.parameters

            config_file = strategy_dir / "config.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False, default=str)
            LOGGER.info(f"  ✅ 配置已保存: {config_file.name}")
        except Exception as e:
            LOGGER.warning(f"  ⚠️  保存配置失败: {e}")

        # 4. 保存回测结果摘要
        if backtest_result is not None:
            try:
                summary = {
                    "final_capital": getattr(backtest_result, "final_capital", 0),
                    "total_return": getattr(backtest_result, "total_return", 0),
                    "annualized_return": getattr(
                        backtest_result, "annualized_return", 0
                    ),
                    "sharpe_ratio": getattr(backtest_result, "sharpe_ratio", 0),
                    "max_drawdown": getattr(backtest_result, "max_drawdown", 0),
                    "total_trades": getattr(backtest_result, "total_trades", 0),
                    "win_rate": getattr(backtest_result, "win_rate", 0),
                    "profit_factor": getattr(backtest_result, "profit_factor", 0),
                }

                result_file = strategy_dir / "backtest_summary.json"
                with open(result_file, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2, default=str)
                LOGGER.info(f"  ✅ 回测结果已保存: {result_file.name}")
            except Exception as e:
                LOGGER.warning(f"  ⚠️  保存回测结果失败: {e}")

        # 5. 创建README
        try:
            readme_content = self._generate_readme(
                strategy_id=strategy_id,
                strategy_code=strategy_code,
                config=config_data,
                backtest_result=backtest_result,
            )

            readme_file = strategy_dir / "README.md"
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(readme_content)
            LOGGER.info(f"  ✅ README已生成: {readme_file.name}")
        except Exception as e:
            LOGGER.warning(f"  ⚠️  生成README失败: {e}")

        LOGGER.info(f"✅ 策略保存完成: {strategy_dir.absolute()}")
        return strategy_id

    def _generate_readme(
        self,
        strategy_id: str,
        strategy_code: Any,
        config: Dict,
        backtest_result: Optional[Any] = None,
    ) -> str:
        """生成README内容"""

        strategy_name = getattr(strategy_code, "strategy_name", "未命名策略")
        model_type = config.get("model_type", "unknown")
        created_at = config.get("created_at", datetime.now().isoformat())

        readme = f"""# 策略: {strategy_id}

## 📊 基本信息

- **策略名称**: {strategy_name}
- **模型类型**: {model_type.upper()}
- **创建时间**: {created_at[:19].replace("T", " ")}
- **版本**: {config.get("version", "1.0.0")}

## 📝 策略描述

{config.get("description", "无描述")}

"""

        # 添加用户需求
        if "user_requirement" in config:
            readme += f"""## 🎯 用户需求

```
{config["user_requirement"]}
```

"""

        # 添加回测表现
        if backtest_result:
            total_return = getattr(backtest_result, "total_return", 0)
            annualized_return = getattr(backtest_result, "annualized_return", 0)
            sharpe_ratio = getattr(backtest_result, "sharpe_ratio", 0)
            max_drawdown = getattr(backtest_result, "max_drawdown", 0)
            total_trades = getattr(backtest_result, "total_trades", 0)
            win_rate = getattr(backtest_result, "win_rate", 0)

            readme += f"""## 📈 回测表现

| 指标 | 数值 |
|------|------|
| 总收益率 | {total_return:.2%} |
| 年化收益率 | {annualized_return:.2%} |
| 夏普比率 | {sharpe_ratio:.2f} |
| 最大回撤 | {max_drawdown:.2%} |
| 交易次数 | {total_trades} |
| 胜率 | {win_rate:.2%} |

"""

        # 添加策略参数
        if "parameters" in config:
            params = config["parameters"]
            readme += """## ⚙️ 策略参数

```json
"""
            readme += json.dumps(params, indent=2, ensure_ascii=False)
            readme += """
```

"""

        # 添加文件说明
        readme += """## 📁 文件说明

- `strategy.py`: 可执行的策略代码
- `model.pth`: 训练好的模型权重（如果有）
- `config.json`: 策略配置参数
- `backtest_summary.json`: 回测结果摘要
- `README.md`: 本说明文件

## 🚀 使用方法

### 方法1: 直接加载
```python
from ai_strategy_system.strategy_persistence import StrategyPersistence

persistence = StrategyPersistence()
strategy = persistence.load_strategy("{strategy_id}")

print(f"策略名称: {{strategy['config']['strategy_name']}}")
print(f"策略代码: {{strategy['strategy_code'][:100]}}...")
```

### 方法2: 重新运行回测
```python
from ai_strategy_system.intelligent_strategy_ai import IntelligentStrategyAI

# 加载配置中的用户需求
ai = IntelligentStrategyAI(user_requirement=strategy['config']['user_requirement'])
await ai.run_intelligent_workflow()
```

## 📊 监控建议

- 定期检查策略表现
- 监控最大回撤是否超过预期
- 关注交易频率和胜率变化
- 在市场环境变化时重新训练

## ⚠️ 风险提示

- 历史表现不代表未来收益
- 建议先用小资金测试
- 注意控制仓位和风险
- 定期review策略有效性

---

**生成工具**: AlgoVoice AI策略系统  
**文档版本**: 1.0  
**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return readme

    def load_strategy_info(self, strategy_id: str) -> Optional[Dict]:
        """加载策略元数据(仅配置信息,不加载模型)

        Args:
            strategy_id: 策略ID

        Returns:
            策略元数据字典，不存在返回None
        """
        strategy_dir = self.base_dir / strategy_id

        if not strategy_dir.exists():
            return None

        result = {
            "strategy_id": strategy_id,
            "strategy_dir": str(strategy_dir.absolute()),
        }

        # 加载配置
        config_file = strategy_dir / "config.json"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                result.update(
                    {
                        "name": config.get("strategy_name", f"策略_{strategy_id}"),
                        "description": config.get("description", ""),
                        "model_type": config.get("model_type", "unknown"),
                        "user_requirement": config.get("user_requirement"),
                        "metadata": config,
                    }
                )

        # 加载股票列表
        if "universe" in result.get("metadata", {}):
            result["stock_symbols"] = result["metadata"]["universe"].get("symbols", [])

        return result

    def load_strategy(self, strategy_id: str) -> Dict:
        """加载策略

        Args:
            strategy_id: 策略ID

        Returns:
            包含策略所有信息的字典
        """
        strategy_dir = self.base_dir / strategy_id

        if not strategy_dir.exists():
            raise FileNotFoundError(f"策略不存在: {strategy_id}")

        LOGGER.info(f"📂 加载策略: {strategy_id}")

        result = {"strategy_id": strategy_id}

        # 加载配置
        config_file = strategy_dir / "config.json"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                result["config"] = json.load(f)
            LOGGER.info("  ✅ 配置已加载")

        # 加载策略代码
        code_file = strategy_dir / "strategy.py"
        if code_file.exists():
            with open(code_file, "r", encoding="utf-8") as f:
                result["strategy_code"] = f.read()
            LOGGER.info("  ✅ 策略代码已加载")

        # 加载模型（如果存在）
        model_file = strategy_dir / "model.pth"
        if model_file.exists():
            try:
                result["model_state"] = torch.load(model_file)
                LOGGER.info("  ✅ 模型权重已加载")
            except Exception as e:
                LOGGER.warning(f"  ⚠️  加载模型失败: {e}")

        # 加载回测结果
        summary_file = strategy_dir / "backtest_summary.json"
        if summary_file.exists():
            with open(summary_file, "r", encoding="utf-8") as f:
                result["backtest_summary"] = json.load(f)
            LOGGER.info("  ✅ 回测摘要已加载")

        LOGGER.info("✅ 策略加载完成")
        return result

    def list_strategies(
        self, limit: int = 20, sort_by: str = "created_at"
    ) -> List[Dict]:
        """列出所有策略

        Args:
            limit: 最多返回数量
            sort_by: 排序字段 (created_at, total_return, sharpe_ratio)

        Returns:
            策略列表
        """
        strategies = []

        for strategy_dir in self.base_dir.iterdir():
            if not strategy_dir.is_dir():
                continue

            config_file = strategy_dir / "config.json"
            summary_file = strategy_dir / "backtest_summary.json"

            if not config_file.exists():
                continue

            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                strategy_info = {
                    "strategy_id": strategy_dir.name,
                    "strategy_name": config.get("strategy_name", "Unknown"),
                    "model_type": config.get("model_type", "unknown"),
                    "created_at": config.get("created_at", ""),
                    "version": config.get("version", "1.0.0"),
                }

                # 添加回测结果
                if summary_file.exists():
                    with open(summary_file, "r", encoding="utf-8") as f:
                        summary = json.load(f)
                        strategy_info["performance"] = summary

                strategies.append(strategy_info)

            except Exception as e:
                LOGGER.warning(f"跳过损坏的策略目录 {strategy_dir.name}: {e}")
                continue

        # 排序
        if sort_by == "created_at":
            strategies.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_by == "total_return":
            strategies.sort(
                key=lambda x: x.get("performance", {}).get("total_return", -999),
                reverse=True,
            )
        elif sort_by == "sharpe_ratio":
            strategies.sort(
                key=lambda x: x.get("performance", {}).get("sharpe_ratio", -999),
                reverse=True,
            )

        return strategies[:limit]

    def delete_strategy(self, strategy_id: str) -> bool:
        """删除策略

        Args:
            strategy_id: 策略ID

        Returns:
            是否删除成功
        """
        strategy_dir = self.base_dir / strategy_id

        if not strategy_dir.exists():
            LOGGER.warning(f"策略不存在: {strategy_id}")
            return False

        try:
            import shutil

            shutil.rmtree(strategy_dir)
            LOGGER.info(f"🗑️  策略已删除: {strategy_id}")
            return True
        except Exception as e:
            LOGGER.error(f"删除策略失败: {e}")
            return False

    def export_strategy(self, strategy_id: str, export_path: str) -> bool:
        """导出策略到指定路径

        Args:
            strategy_id: 策略ID
            export_path: 导出路径

        Returns:
            是否导出成功
        """
        strategy_dir = self.base_dir / strategy_id

        if not strategy_dir.exists():
            LOGGER.warning(f"策略不存在: {strategy_id}")
            return False

        try:
            import shutil

            export_dir = Path(export_path)
            shutil.copytree(strategy_dir, export_dir / strategy_id)
            LOGGER.info(f"📦 策略已导出到: {export_dir / strategy_id}")
            return True
        except Exception as e:
            LOGGER.error(f"导出策略失败: {e}")
            return False


def create_strategy_persistence(base_dir: Optional[str] = None) -> StrategyPersistence:
    """工厂函数：创建策略持久化管理器"""
    if base_dir:
        return StrategyPersistence(base_dir)
    return StrategyPersistence()


# CLI工具
if __name__ == "__main__":
    import sys

    persistence = StrategyPersistence()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            print("\n📋 所有已保存的策略:\n")
            strategies = persistence.list_strategies(limit=20)

            for i, strategy in enumerate(strategies, 1):
                print(f"{i}. {strategy['strategy_id']}")
                print(f"   名称: {strategy['strategy_name']}")
                print(f"   模型: {strategy['model_type']}")
                print(f"   创建时间: {strategy['created_at'][:19]}")

                if "performance" in strategy:
                    perf = strategy["performance"]
                    print(f"   总收益: {perf.get('total_return', 0):.2%}")
                    print(f"   夏普比率: {perf.get('sharpe_ratio', 0):.2f}")
                print()

            print(f"总计: {len(strategies)} 个策略\n")

        elif command == "load" and len(sys.argv) > 2:
            strategy_id = sys.argv[2]
            strategy = persistence.load_strategy(strategy_id)

            print(f"\n✅ 已加载策略: {strategy_id}")
            print(
                f"配置: {json.dumps(strategy.get('config', {}), indent=2, ensure_ascii=False)}"
            )

        elif command == "delete" and len(sys.argv) > 2:
            strategy_id = sys.argv[2]
            if persistence.delete_strategy(strategy_id):
                print(f"\n✅ 已删除策略: {strategy_id}")
            else:
                print(f"\n❌ 删除失败: {strategy_id}")

        else:
            print("未知命令")

    else:
        print("""
AlgoVoice 策略持久化管理器

使用方法:
  python strategy_persistence.py list              # 列出所有策略
  python strategy_persistence.py load <strategy_id> # 加载策略
  python strategy_persistence.py delete <strategy_id> # 删除策略
""")
