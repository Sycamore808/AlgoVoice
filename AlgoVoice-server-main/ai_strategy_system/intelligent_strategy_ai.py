#!/usr/bin/env python3
"""
完全智能化的AI策略系统
用户只需输入投资需求，系统自动完成：
1. 市场分析和状态判断
2. 智能选股推荐
3. 自动选择最优AI模型
4. 策略自动生成和优化
5. 回测和报告生成
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from common.data_structures import Signal
from common.logging_system import setup_logger

# ========== 完整的模块导入 ==========
# Module 01: 数据
from module_01_data_pipeline import AkshareDataCollector, get_database_manager

# Module 02: 特征工程
from module_02_feature_engineering import TechnicalIndicators

# Module 03: AI模型（多种模型）
from module_03_ai_models import (
    EnsembleConfig,
    EnsemblePredictor,
    LSTMModel,
    LSTMModelConfig,
    OnlineLearner,
    OnlineLearningConfig,
    PPOAgent,
    PPOConfig,
    TradingEnvironment,
    TransformerConfig,
    TransformerPredictor,
    get_ai_model_database_manager,
)

# Module 04: 市场分析（AI分析市场）
from module_04_market_analysis.regime_detection.market_regime_detector import (
    MarketRegimeDetector,
    RegimeDetectionConfig,
)
from module_04_market_analysis.sentiment_analysis.fin_r1_sentiment import (
    TradingAgentsSentimentAnalyzer,
)

# Module 05: 风险管理
from module_05_risk_management.portfolio_optimization.mean_variance_optimizer import (
    MeanVarianceOptimizer,
)

# Module 09: 回测
from module_09_backtesting import (
    BacktestConfig,
    BacktestEngine,
    BacktestReportGenerator,
    PerformanceAnalyzer,
    ReportConfig,
)

# Module 10: AI交互和推荐
from module_10_ai_interaction import (
    RecommendationEngine,
    RequirementParser,
)

logger = setup_logger("intelligent_strategy_ai")


class IntelligentStrategyAI:
    """完全智能化的AI策略系统"""

    def __init__(
        self, user_requirement: str = None, initial_capital: float = 1000000.0
    ):
        """
        初始化智能策略系统

        Args:
            user_requirement: 用户需求（自然语言），如"我想要稳健成长的策略"
            initial_capital: 初始资金
        """
        self.user_requirement = user_requirement or "中等风险，追求稳健收益"
        self.initial_capital = initial_capital

        # AI组件
        self.requirement_parser = None
        self.recommendation_engine = None
        self.market_regime_detector = None
        self.sentiment_analyzer = None

        # 数据容器
        self.parsed_requirement = None
        self.market_analysis = {}
        self.recommended_stocks = []
        self.selected_model = None
        self.strategy_config = {}

        logger.info("=" * 60)
        logger.info("🤖 智能策略AI系统初始化")
        logger.info("=" * 60)
        logger.info(f"用户需求: {self.user_requirement}")
        logger.info(f"初始资金: ¥{self.initial_capital:,.0f}")

    async def step1_understand_requirement(self):
        """步骤1: AI理解用户需求 (Module 10)"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤1: AI理解用户需求 (Module 10 - NLP)")
        logger.info("=" * 60)

        try:
            # 使用Module 10的需求解析器
            self.requirement_parser = RequirementParser()

            # 解析用户自然语言需求
            logger.info(f"正在解析需求: '{self.user_requirement}'")
            self.parsed_requirement = self.requirement_parser.parse_requirement(
                self.user_requirement
            )

            logger.info("\n✓ 需求解析结果:")
            logger.info(
                f"  投资金额: ¥{self.parsed_requirement.investment_amount:,.0f}"
            )
            logger.info(f"  风险偏好: {self.parsed_requirement.risk_tolerance}")
            logger.info(f"  投资期限: {self.parsed_requirement.investment_horizon}")
            logger.info(f"  投资目标: {self.parsed_requirement.goals}")

            # 映射到系统参数
            self.strategy_config = self.requirement_parser.map_to_system_parameters(
                self.parsed_requirement
            )
            logger.info(f"\n✓ 系统参数映射完成")

            return True

        except Exception as e:
            logger.error(f"✗ 需求解析失败: {e}")
            # 使用默认配置
            self.strategy_config = {
                "risk_params": {"max_position_size": 0.3, "stop_loss": 0.05},
                "strategy_params": {"holding_period": "medium"},
            }
            logger.info("使用默认配置")
            return True

    async def step2_analyze_market(self):
        """步骤2: AI分析市场状态 (Module 04)"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤2: AI分析市场状态 (Module 04 - 多维分析)")
        logger.info("=" * 60)

        try:
            collector = AkshareDataCollector(rate_limit=0.5)

            # 2.1 市场状态检测
            logger.info("\n[2.1] 检测市场状态...")
            self.market_regime_detector = MarketRegimeDetector(
                RegimeDetectionConfig(n_regimes=3, use_hmm=True, use_clustering=True)
            )

            # 获取主要市场指数数据
            index_symbol = "000300"  # 沪深300
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=252)).strftime("%Y%m%d")

            market_data = collector.fetch_stock_history(
                index_symbol, start_date, end_date
            )

            if not market_data.empty:
                regime_state = self.market_regime_detector.detect_market_regime(
                    market_data
                )
                self.market_analysis["regime"] = {
                    "state": regime_state.regime.value,
                    "confidence": regime_state.confidence,
                    "characteristics": regime_state.characteristics,
                }
                logger.info(f"✓ 市场状态: {regime_state.regime.value}")
                logger.info(f"  置信度: {regime_state.confidence:.2%}")
            else:
                logger.warning("⚠ 无法获取市场数据，使用默认状态")
                self.market_analysis["regime"] = {"state": "neutral", "confidence": 0.5}

            # 2.2 情感分析
            logger.info("\n[2.2] 分析市场情感...")
            self.sentiment_analyzer = TradingAgentsSentimentAnalyzer()

            try:
                # 分析整体市场情感
                market_sentiment = (
                    await self.sentiment_analyzer.analyze_market_sentiment()
                )
                self.market_analysis["sentiment"] = {
                    "score": market_sentiment.get("overall_sentiment", 0),
                    "confidence": market_sentiment.get("confidence", 0.5),
                }
                logger.info(
                    f"✓ 市场情感: {market_sentiment.get('overall_sentiment', 0):.2f}"
                )
            except Exception as e:
                logger.warning(f"⚠ 情感分析失败: {e}，使用中性情感")
                self.market_analysis["sentiment"] = {"score": 0, "confidence": 0.5}

            # 2.3 生成市场总结
            market_state = self.market_analysis["regime"]["state"]
            sentiment_score = self.market_analysis["sentiment"]["score"]

            logger.info("\n✓ 市场分析完成:")
            logger.info(f"  市场状态: {market_state}")
            logger.info(f"  市场情感: {sentiment_score:.2f}")

            return True

        except Exception as e:
            logger.error(f"✗ 市场分析失败: {e}")
            import traceback

            traceback.print_exc()
            # 使用默认分析结果
            self.market_analysis = {
                "regime": {"state": "neutral", "confidence": 0.5},
                "sentiment": {"score": 0, "confidence": 0.5},
            }
            return True

    async def step3_ai_select_stocks(self):
        """步骤3: AI智能选股 (Module 10 推荐引擎)"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤3: AI智能选股 (Module 10 - 推荐引擎)")
        logger.info("=" * 60)

        try:
            self.recommendation_engine = RecommendationEngine()

            # 根据解析的需求和市场状态生成股票推荐
            user_profile = {
                "risk_tolerance": (
                    str(self.parsed_requirement.risk_tolerance)
                    if self.parsed_requirement
                    else "moderate"
                ),
                "investment_horizon": (
                    str(self.parsed_requirement.investment_horizon)
                    if self.parsed_requirement
                    else "medium_term"
                ),
                "goals": ["wealth_growth"],
            }

            market_conditions = {
                "trend": self.market_analysis["regime"]["state"],
                "volatility": "medium",
                "sentiment": self.market_analysis["sentiment"]["score"],
            }

            logger.info("正在生成投资组合推荐...")

            # 获取推荐组合
            portfolio_recommendations = (
                self.recommendation_engine.generate_portfolio_recommendations(
                    user_profile=user_profile,
                    market_conditions=market_conditions,
                    num_recommendations=3,
                )
            )

            if portfolio_recommendations:
                best_portfolio = portfolio_recommendations[0]
                logger.info(f"\n✓ 推荐组合: {best_portfolio.name}")
                logger.info(f"  适合度评分: {best_portfolio.suitability_score:.2f}")
                logger.info(
                    f"  预期收益: {best_portfolio.expected_metrics.get('expected_return', 0):.2%}"
                )

                # 从推荐的资产配置中提取股票
                # 这里简化处理，实际应该根据asset_allocation动态选择
                self.recommended_stocks = self._map_allocation_to_stocks(
                    best_portfolio.asset_allocation
                )
            else:
                # 如果推荐失败，使用默认股票池
                logger.warning("⚠ 推荐失败，使用默认股票池")
                self.recommended_stocks = self._get_default_stock_pool()

            logger.info(f"\n✓ 选定股票池 ({len(self.recommended_stocks)}只):")
            for symbol in self.recommended_stocks:
                logger.info(f"  - {symbol}")

            return True

        except Exception as e:
            logger.error(f"✗ AI选股失败: {e}")
            import traceback

            traceback.print_exc()
            self.recommended_stocks = self._get_default_stock_pool()
            logger.info(f"使用默认股票池: {self.recommended_stocks}")
            return True

    def _map_allocation_to_stocks(self, allocation: Dict[str, float]) -> List[str]:
        """将资产配置映射到具体股票"""
        stocks = []

        # 根据配置映射到具体板块和股票
        stock_mapping = {
            "stocks": ["600036", "000858", "600519"],  # 大盘蓝筹
            "dividend_stocks": ["601318", "600028"],  # 高股息
            "growth_stocks": ["000001", "002594"],  # 成长股
            "tech": ["000063", "002475"],  # 科技股
        }

        for asset_type, weight in allocation.items():
            if weight > 0 and asset_type in stock_mapping:
                # 按权重选择股票数量
                num_stocks = max(1, int(weight * 10))
                stocks.extend(stock_mapping[asset_type][:num_stocks])

        # 去重并限制数量
        stocks = list(set(stocks))[:8]  # 最多8只股票

        # 如果为空，返回默认
        return stocks if stocks else self._get_default_stock_pool()

    def _get_default_stock_pool(self) -> List[str]:
        """获取默认股票池"""
        return ["000001", "600036", "000858", "600519", "601318"]

    async def step4_ai_select_model(self):
        """步骤4: AI自动选择最优模型 (Module 03)"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤4: AI自动选择最优模型 (Module 03)")
        logger.info("=" * 60)

        try:
            market_state = self.market_analysis["regime"]["state"]
            sentiment = self.market_analysis["sentiment"]["score"]

            # 根据市场状态和风险偏好智能选择模型
            logger.info(f"根据市场状态 [{market_state}] 选择最优AI模型...")

            model_selection = self._intelligent_model_selection(market_state, sentiment)

            self.selected_model_type = model_selection["type"]
            self.selected_model_config = model_selection["config"]
            self.selected_model_reason = model_selection["reason"]

            logger.info(f"\n✓ 选择模型: {self.selected_model_type}")
            logger.info(f"  原因: {self.selected_model_reason}")
            logger.info(f"  配置: {self.selected_model_config}")

            return True

        except Exception as e:
            logger.error(f"✗ 模型选择失败: {e}")
            # 默认使用LSTM
            self.selected_model_type = "lstm"
            self.selected_model_config = {"sequence_length": 10, "hidden_size": 32}
            return True

    def _intelligent_model_selection(
        self, market_state: str, sentiment: float
    ) -> Dict[str, Any]:
        """智能模型选择算法"""

        # 根据市场状态选择模型
        if market_state == "bull":
            # 牛市：使用动量策略，LSTM效果好
            return {
                "type": "lstm",
                "config": {
                    "sequence_length": 10,
                    "hidden_size": 64,
                    "num_layers": 2,
                    "epochs": 15,
                },
                "reason": "牛市行情，LSTM捕捉趋势效果好",
            }
        elif market_state == "bear":
            # 熊市：使用防御策略，在线学习快速适应
            return {
                "type": "online",
                "config": {"learning_rate": 0.01, "buffer_size": 500},
                "reason": "熊市震荡，在线学习快速适应市场变化",
            }
        elif abs(sentiment) > 0.5:
            # 情绪极端：使用强化学习
            return {
                "type": "ppo",
                "config": {"learning_rate": 0.0003, "hidden_dims": [64, 64]},
                "reason": "市场情绪极端，强化学习应对复杂环境",
            }
        else:
            # 震荡市：使用集成模型
            return {
                "type": "ensemble",
                "config": {"models": ["lstm", "transformer"], "voting": "weighted"},
                "reason": "震荡市场，集成模型提高稳定性",
            }

    async def step5_train_selected_model(self):
        """步骤5: 训练选定的AI模型"""
        logger.info("\n" + "=" * 60)
        logger.info(f"步骤5: 训练{self.selected_model_type.upper()}模型")
        logger.info("=" * 60)

        try:
            # 获取数据
            collector = AkshareDataCollector(rate_limit=0.5)
            calculator = TechnicalIndicators()

            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

            all_features = []

            for symbol in self.recommended_stocks:
                try:
                    data = collector.fetch_stock_history(symbol, start_date, end_date)
                    if data is not None and not data.empty:
                        features = calculator.calculate_all_indicators(data)
                        features["returns"] = features["close"].pct_change()
                        features["future_returns"] = features["returns"].shift(-1)
                        features["symbol"] = symbol
                        features = features.dropna()
                        all_features.append(features)
                        logger.info(f"✓ {symbol}: {len(features)} 条记录")
                except Exception as e:
                    logger.warning(f"⚠ {symbol} 数据获取失败: {e}")

            if not all_features:
                logger.error("无可用数据")
                return False

            combined_features = pd.concat(all_features, ignore_index=True)
            train_size = int(0.8 * len(combined_features))
            train_data = combined_features[:train_size]

            logger.info(f"\n训练数据: {len(train_data)} 条")

            # 根据选择的模型类型训练
            if self.selected_model_type == "lstm":
                self.trained_model = await self._train_lstm_model(train_data)
            elif self.selected_model_type == "online":
                self.trained_model = await self._train_online_model(train_data)
            elif self.selected_model_type == "ppo":
                self.trained_model = await self._train_ppo_model(train_data)
            elif self.selected_model_type == "ensemble":
                self.trained_model = await self._train_ensemble_model(train_data)
            else:
                # 默认LSTM
                self.trained_model = await self._train_lstm_model(train_data)

            logger.info("✓ 模型训练完成")
            return True

        except Exception as e:
            logger.error(f"✗ 模型训练失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def _train_lstm_model(self, train_data: pd.DataFrame):
        """训练LSTM模型"""
        config = LSTMModelConfig(
            sequence_length=self.selected_model_config.get("sequence_length", 10),
            hidden_size=self.selected_model_config.get("hidden_size", 32),
            num_layers=self.selected_model_config.get("num_layers", 1),
            epochs=self.selected_model_config.get("epochs", 10),
            batch_size=16,
            learning_rate=0.001,
        )

        model = LSTMModel(config)
        X, y = model.prepare_data(
            train_data.drop(columns=["symbol"], errors="ignore"), "future_returns"
        )
        model.train(X, y)
        return model

    async def _train_online_model(self, train_data: pd.DataFrame):
        """训练在线学习模型"""
        config = OnlineLearningConfig(
            learning_rate=self.selected_model_config.get("learning_rate", 0.01),
            buffer_size=self.selected_model_config.get("buffer_size", 500),
        )

        model = OnlineLearner(config)

        # 逐步添加样本
        features = train_data.drop(
            columns=["symbol", "future_returns"], errors="ignore"
        ).values
        targets = train_data["future_returns"].values

        for feat, target in zip(features[:1000], targets[:1000]):
            model.add_sample(feat, target)

        return model

    async def _train_ppo_model(self, train_data: pd.DataFrame):
        """训练PPO强化学习模型"""
        # 创建交易环境
        env_data = train_data.copy()

        config = PPOConfig(
            state_dim=10,
            action_dim=3,
            learning_rate=self.selected_model_config.get("learning_rate", 0.0003),
        )

        model = PPOAgent(config)

        # 简化训练（实际需要更复杂的环境）
        logger.info("PPO模型创建完成（简化版本）")
        return model

    async def _train_ensemble_model(self, train_data: pd.DataFrame):
        """训练集成模型"""
        logger.info("训练集成模型...")

        # 创建LSTM
        lstm_model = await self._train_lstm_model(train_data)

        # 创建简单的集成
        config = EnsembleConfig(
            models=[{"name": "lstm", "model": lstm_model, "weight": 1.0}],
            voting_strategy="weighted",
        )

        ensemble = EnsemblePredictor(config)
        return ensemble

    async def step6_generate_strategy(self):
        """步骤6: 自动生成交易策略"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤6: 自动生成交易策略")
        logger.info("=" * 60)

        # 根据市场状态和模型类型生成策略参数
        market_state = self.market_analysis["regime"]["state"]

        if market_state == "bull":
            self.strategy_params = {
                "buy_threshold": 0.001,
                "confidence_threshold": 0.5,
                "max_position": 0.4,
            }
            logger.info("✓ 生成策略: 牛市激进策略")
        elif market_state == "bear":
            self.strategy_params = {
                "buy_threshold": 0.003,
                "confidence_threshold": 0.7,
                "max_position": 0.2,
            }
            logger.info("✓ 生成策略: 熊市防御策略")
        else:
            self.strategy_params = {
                "buy_threshold": 0.002,
                "confidence_threshold": 0.6,
                "max_position": 0.3,
            }
            logger.info("✓ 生成策略: 平衡策略")

        logger.info(f"  买入阈值: {self.strategy_params['buy_threshold']:.3%}")
        logger.info(f"  置信度要求: {self.strategy_params['confidence_threshold']:.1%}")
        logger.info(f"  最大仓位: {self.strategy_params['max_position']:.1%}")

        return True

    async def step7_run_backtest(self):
        """步骤7: 运行智能回测"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤7: 运行智能回测 (Module 09)")
        logger.info("=" * 60)

        try:
            # 准备市场数据
            collector = AkshareDataCollector(rate_limit=0.5)
            calculator = TechnicalIndicators()

            market_data = {}
            features_data = {}

            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

            for symbol in self.recommended_stocks:
                try:
                    data = collector.fetch_stock_history(symbol, start_date, end_date)
                    if data is not None and not data.empty:
                        market_data[symbol] = data
                        features = calculator.calculate_all_indicators(data)
                        features["symbol"] = symbol
                        features_data[symbol] = features
                except:
                    continue

            if not market_data:
                logger.error("无市场数据")
                return False

            # 创建AI策略函数
            def ai_strategy(current_data, positions, capital):
                signals = []
                try:
                    for symbol, data in current_data.items():
                        if symbol in positions:
                            continue

                        features = features_data.get(symbol)
                        if features is None or len(features) < 10:
                            continue

                        recent = features.tail(10).drop(
                            columns=["symbol"], errors="ignore"
                        )
                        if recent.empty:
                            continue

                        # AI预测
                        try:
                            prediction = self.trained_model.predict(recent.values[-5:])
                            pred_return = (
                                prediction.predictions[0]
                                if hasattr(prediction, "predictions")
                                else prediction
                            )
                            confidence = getattr(prediction, "confidence", 0.7)
                        except:
                            continue

                        # 使用动态阈值
                        if (
                            pred_return > self.strategy_params["buy_threshold"]
                            and confidence
                            > self.strategy_params["confidence_threshold"]
                        ):
                            price = data["close"]
                            position_value = (
                                capital
                                * self.strategy_params["max_position"]
                                * confidence
                            )
                            quantity = int(position_value / price / 100) * 100

                            if quantity >= 100:
                                signal = Signal(
                                    signal_id=f"ai_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                    symbol=symbol,
                                    signal_type="BUY",
                                    price=price,
                                    quantity=quantity,
                                    confidence=confidence,
                                    timestamp=datetime.now(),
                                    strategy_name="智能AI策略",
                                    metadata={"predicted_return": float(pred_return)},
                                )
                                signals.append(signal)
                                break
                except:
                    pass
                return signals

            # 配置回测
            config = BacktestConfig(
                start_date=datetime.strptime(start_date, "%Y%m%d"),
                end_date=datetime.strptime(end_date, "%Y%m%d"),
                initial_capital=self.initial_capital,
                commission_rate=0.0003,
                slippage_bps=5.0,
                save_to_db=True,
                strategy_name=f"智能AI策略-{self.selected_model_type.upper()}",
            )

            # 运行回测
            engine = BacktestEngine(config)
            engine.load_market_data(list(market_data.keys()), market_data)
            engine.set_strategy(ai_strategy)

            logger.info("开始回测...")
            result = engine.run()

            # 显示结果
            logger.info("\n" + "=" * 60)
            logger.info("✓ 回测完成!")
            logger.info("=" * 60)
            logger.info(f"总收益率:    {result.total_return:>12.2%}")
            logger.info(f"年化收益率:  {result.annualized_return:>12.2%}")
            logger.info(f"夏普比率:    {result.sharpe_ratio:>12.3f}")
            logger.info(f"最大回撤:    {result.max_drawdown:>12.2%}")
            logger.info(f"交易次数:    {result.total_trades:>12}")
            logger.info(f"胜率:        {result.win_rate:>12.2%}")

            self.backtest_result = result
            self.backtest_id = engine.backtest_id

            # 生成报告
            report_config = ReportConfig(
                title=f"智能AI策略回测报告 - {self.selected_model_type.upper()}",
                formats=["html", "excel"],
                output_dir="reports",
            )

            report_gen = BacktestReportGenerator(report_config)
            report_files = report_gen.generate_report(backtest_result=result)

            logger.info("\n报告已生成:")
            for fmt, path in report_files.items():
                logger.info(f"  {fmt.upper()}: {path}")

            return True

        except Exception as e:
            logger.error(f"✗ 回测失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def run_intelligent_workflow(self):
        """运行完整的智能工作流"""
        logger.info("\n")
        logger.info("🤖 " + "=" * 56 + " 🤖")
        logger.info("🤖  完全智能化AI策略系统  🤖")
        logger.info("🤖 " + "=" * 56 + " 🤖")

        steps = [
            ("AI理解用户需求", self.step1_understand_requirement),
            ("AI分析市场状态", self.step2_analyze_market),
            ("AI智能选股", self.step3_ai_select_stocks),
            ("AI选择最优模型", self.step4_ai_select_model),
            ("训练AI模型", self.step5_train_selected_model),
            ("生成交易策略", self.step6_generate_strategy),
            ("运行智能回测", self.step7_run_backtest),
        ]

        for i, (name, func) in enumerate(steps, 1):
            try:
                success = await func()
                if not success:
                    logger.error(f"\n❌ 步骤{i}失败: {name}")
                    return False
            except Exception as e:
                logger.error(f"\n❌ 步骤{i}异常: {name} - {e}")
                import traceback

                traceback.print_exc()
                return False

        logger.info("\n" + "=" * 60)
        logger.info("✅ 智能AI策略完整流程执行成功!")
        logger.info("=" * 60)
        logger.info(f"\n回测ID: {self.backtest_id}")
        logger.info(f"选用模型: {self.selected_model_type.upper()}")
        logger.info(f"股票数量: {len(self.recommended_stocks)}")
        logger.info(f"最终收益率: {self.backtest_result.total_return:.2%}")

        return True


async def main():
    """主函数"""

    print("\n" + "=" * 70)
    print("🤖  AlgoVoice 智能AI策略系统  🤖")
    print("=" * 70)

    # 从命令行获取需求
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(f"\n📝 用户需求: {user_input}")
    else:
        user_input = "我想要一个中等风险的策略，追求稳健收益，投资期限1-2年"
        print(f"\n📝 默认需求: {user_input}")
        print('💡 可自定义: python intelligent_strategy_ai.py "您的需求"\n')

    print("\n系统将自动完成:")
    print("  1. 理解投资需求")
    print("  2. 分析市场状态")
    print("  3. 智能推荐股票")
    print("  4. 选择最优AI模型")
    print("  5. 训练模型生成策略")
    print("  6. 运行回测生成报告")
    print("\n⏱️  预计耗时: 5-10分钟")
    print("=" * 70 + "\n")

    try:
        ai_system = IntelligentStrategyAI(
            user_requirement=user_input, initial_capital=1000000.0
        )

        success = await ai_system.run_intelligent_workflow()

        if success:
            print("\n" + "=" * 70)
            print("✅ 所有任务完成!")
            print("=" * 70)
            print(f"\n📊 结果:")
            print(f"  回测ID: {ai_system.backtest_id}")
            print(f"  选用模型: {ai_system.selected_model_type.upper()}")
            print(f"  股票数量: {len(ai_system.recommended_stocks)}")
            print(f"  收益率: {ai_system.backtest_result.total_return:.2%}")
            print(f"  夏普比率: {ai_system.backtest_result.sharpe_ratio:.3f}")
            print(f"  最大回撤: {ai_system.backtest_result.max_drawdown:.2%}")
            print("\n📁 报告: reports/ 目录")
            print("=" * 70)
        else:
            print("\n❌ 执行失败，查看日志")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
