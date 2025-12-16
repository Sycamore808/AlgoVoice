#!/usr/bin/env python3
"""每日运行器 - 定时运行策略并生成投资信号"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Dict, List

import schedule

from ai_strategy_system.services.live_trading_manager import LiveTradingManager
from ai_strategy_system.services.notification_system import NotificationSystem
from ai_strategy_system.services.signal_generator import SignalGenerator
from common.logging_system import setup_logger

LOGGER = setup_logger("daily_runner")


class DailyRunner:
    """每日运行器

    功能:
    1. 定时任务调度
    2. 检查交易时间
    3. 生成交易信号
    4. 发送通知
    5. 更新账户状态
    """

    def __init__(self):
        """初始化每日运行器"""
        self.signal_generator = SignalGenerator()
        self.manager = LiveTradingManager()
        self.notifier = NotificationSystem()
        LOGGER.info("🚀 每日运行器初始化完成")

    def run_daily_task(self) -> None:
        """运行每日任务"""
        try:
            LOGGER.info("=" * 60)
            LOGGER.info(f"📅 开始执行每日任务: {datetime.now()}")
            LOGGER.info("=" * 60)

            # 1. 检查交易日
            if not self._is_trading_day():
                LOGGER.info("⏸️  今天不是交易日，跳过")
                return

            # 2. 获取所有活跃策略
            active_strategies = self.manager.get_active_strategies()

            if not active_strategies:
                LOGGER.info("📋 暂无活跃策略")
                return

            LOGGER.info(f"📊 活跃策略数量: {len(active_strategies)}")

            # 3. 为每个策略生成信号
            all_results = {}

            for strategy_config in active_strategies:
                strategy_id = strategy_config["strategy_id"]

                try:
                    LOGGER.info(f"\n{'=' * 40}")
                    LOGGER.info(f"📡 处理策略: {strategy_id}")
                    LOGGER.info(f"{'=' * 40}")

                    # 检查交易时间
                    if not self._is_trading_time(strategy_config):
                        LOGGER.info(f"⏰ 不在交易时间内，跳过")
                        continue

                    # 风险检查
                    risk_check = self.manager.check_risk_limits(strategy_id)

                    if not risk_check["passed"]:
                        LOGGER.warning(f"⚠️ 风险检查未通过:")
                        for violation in risk_check["violations"]:
                            LOGGER.warning(f"   - {violation}")

                        # 发送风险告警
                        self.notifier.send_risk_alert(
                            strategy_id=strategy_id, violations=risk_check["violations"]
                        )

                        # 自动暂停策略
                        self.manager.pause_strategy(
                            strategy_id=strategy_id,
                            reason=f"触发风险限制: {risk_check['violations']}",
                        )

                        continue

                    # 生成信号
                    signals = self.signal_generator.generate_signals_for_strategy(
                        strategy_id
                    )

                    if not signals:
                        LOGGER.info(f"📭 无交易信号")
                        all_results[strategy_id] = {
                            "status": "no_signals",
                            "signals": [],
                        }
                        continue

                    LOGGER.info(f"✅ 生成 {len(signals)} 个交易信号")

                    # 发送信号通知
                    self._send_signal_notifications(
                        strategy_config=strategy_config, signals=signals
                    )

                    all_results[strategy_id] = {
                        "status": "success",
                        "signals": signals,
                        "signal_count": len(signals),
                    }

                except Exception as e:
                    LOGGER.error(f"❌ 处理策略 {strategy_id} 失败: {e}", exc_info=True)
                    all_results[strategy_id] = {"status": "error", "error": str(e)}

            # 4. 生成日报
            self._generate_daily_report(all_results)

            LOGGER.info("=" * 60)
            LOGGER.info(f"✅ 每日任务完成: {datetime.now()}")
            LOGGER.info("=" * 60)

        except Exception as e:
            LOGGER.error(f"❌ 每日任务执行失败: {e}", exc_info=True)

    def run_scheduler(self) -> None:
        """运行调度器

        设置定时任务：
        - 每天早上 9:00 运行
        - 每天下午 14:00 运行（追加信号）
        - 每天晚上 21:00 运行（日报）
        """
        LOGGER.info("⏰ 设置定时任务:")

        # 早盘信号 - 9:00
        schedule.every().day.at("09:00").do(self.run_daily_task)
        LOGGER.info("   - 每日 09:00 生成交易信号")

        # 午盘信号 - 14:00
        schedule.every().day.at("14:00").do(self.run_daily_task)
        LOGGER.info("   - 每日 14:00 更新交易信号")

        # 收盘日报 - 21:00
        schedule.every().day.at("21:00").do(self.generate_daily_summary)
        LOGGER.info("   - 每日 21:00 生成日报")

        LOGGER.info("\n🚀 调度器启动，等待任务执行...")

        # 持续运行
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次

            except KeyboardInterrupt:
                LOGGER.info("\n⏸️  调度器已停止")
                break
            except Exception as e:
                LOGGER.error(f"❌ 调度器错误: {e}", exc_info=True)
                time.sleep(60)

    def generate_daily_summary(self) -> None:
        """生成每日摘要"""
        try:
            LOGGER.info("=" * 60)
            LOGGER.info(f"📊 生成每日摘要: {datetime.now()}")
            LOGGER.info("=" * 60)

            active_strategies = self.manager.get_active_strategies()

            summary_data = []

            for strategy_config in active_strategies:
                strategy_id = strategy_config["strategy_id"]

                try:
                    # 获取账户状态
                    account = self.manager.get_account_status(strategy_id)

                    if not account:
                        continue

                    # 获取今日信号
                    today_signals = self.manager.get_signals(
                        strategy_id=strategy_id, days=1
                    )

                    summary_data.append(
                        {
                            "strategy_id": strategy_id,
                            "strategy_name": strategy_config["strategy_name"],
                            "account": account,
                            "signals_count": len(today_signals),
                        }
                    )

                except Exception as e:
                    LOGGER.error(f"❌ 获取 {strategy_id} 摘要失败: {e}")
                    continue

            # 发送日报
            self.notifier.send_daily_summary(summary_data)

            LOGGER.info("✅ 每日摘要生成完成")

        except Exception as e:
            LOGGER.error(f"❌ 生成每日摘要失败: {e}", exc_info=True)

    def _is_trading_day(self) -> bool:
        """检查是否为交易日

        Returns:
            是否为交易日
        """
        # 简单实现：排除周末
        weekday = datetime.now().weekday()

        if weekday >= 5:  # 周六、周日
            return False

        # TODO: 可以调用API检查节假日
        # 比如：使用tushare或akshare获取交易日历

        return True

    def _is_trading_time(self, strategy_config: Dict) -> bool:
        """检查是否在交易时间内

        Args:
            strategy_config: 策略配置

        Returns:
            是否在交易时间内
        """
        trading_hours = strategy_config.get("trading_hours", {})

        if not trading_hours:
            return True  # 如果没有设置，默认任何时间都可以

        now = datetime.now()
        current_time = now.strftime("%H:%M")

        start_time = trading_hours.get("start", "09:30")
        end_time = trading_hours.get("end", "15:00")

        if start_time <= current_time <= end_time:
            return True

        return False

    def _send_signal_notifications(self, strategy_config: Dict, signals: List) -> None:
        """发送信号通知

        Args:
            strategy_config: 策略配置
            signals: 交易信号列表
        """
        try:
            # 获取通知渠道
            channels = strategy_config.get("notification_channels", ["email"])

            # 准备通知内容
            notification_data = {
                "strategy_id": strategy_config["strategy_id"],
                "strategy_name": strategy_config["strategy_name"],
                "signals": signals,
                "timestamp": datetime.now().isoformat(),
            }

            # 发送通知
            for channel in channels:
                try:
                    if channel == "email":
                        self.notifier.send_email_notification(notification_data)
                    elif channel == "wechat":
                        self.notifier.send_wechat_notification(notification_data)
                    elif channel == "dingtalk":
                        self.notifier.send_dingtalk_notification(notification_data)
                    elif channel == "sms":
                        self.notifier.send_sms_notification(notification_data)

                except Exception as e:
                    LOGGER.error(f"❌ 发送 {channel} 通知失败: {e}")

        except Exception as e:
            LOGGER.error(f"❌ 发送通知失败: {e}", exc_info=True)

    def _generate_daily_report(self, results: Dict) -> None:
        """生成每日报告

        Args:
            results: 执行结果
        """
        try:
            LOGGER.info("\n" + "=" * 60)
            LOGGER.info("📈 每日执行报告")
            LOGGER.info("=" * 60)

            total_strategies = len(results)
            success_count = sum(1 for r in results.values() if r["status"] == "success")
            no_signal_count = sum(
                1 for r in results.values() if r["status"] == "no_signals"
            )
            error_count = sum(1 for r in results.values() if r["status"] == "error")
            total_signals = sum(
                r.get("signal_count", 0)
                for r in results.values()
                if r["status"] == "success"
            )

            LOGGER.info(f"策略总数: {total_strategies}")
            LOGGER.info(f"  - 成功: {success_count}")
            LOGGER.info(f"  - 无信号: {no_signal_count}")
            LOGGER.info(f"  - 失败: {error_count}")
            LOGGER.info(f"信号总数: {total_signals}")

            # 详细结果
            LOGGER.info("\n详细结果:")
            for strategy_id, result in results.items():
                status = result["status"]

                if status == "success":
                    LOGGER.info(f"  ✅ {strategy_id}: {result['signal_count']} 个信号")
                elif status == "no_signals":
                    LOGGER.info(f"  📭 {strategy_id}: 无信号")
                elif status == "error":
                    LOGGER.info(f"  ❌ {strategy_id}: {result['error']}")

            LOGGER.info("=" * 60)

        except Exception as e:
            LOGGER.error(f"❌ 生成报告失败: {e}", exc_info=True)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="AlgoVoice每日运行器")
    parser.add_argument(
        "--mode",
        choices=["once", "schedule"],
        default="once",
        help="运行模式: once=立即运行一次, schedule=定时调度",
    )

    args = parser.parse_args()

    runner = DailyRunner()

    if args.mode == "once":
        LOGGER.info("🚀 立即执行一次")
        runner.run_daily_task()
    else:
        LOGGER.info("⏰ 启动定时调度")
        runner.run_scheduler()


if __name__ == "__main__":
    main()
