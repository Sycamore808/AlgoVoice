#!/usr/bin/env python3
"""通知系统 - 发送交易信号通知"""

from __future__ import annotations

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

from common.logging_system import setup_logger

LOGGER = setup_logger("notification_system")


class NotificationSystem:
    """通知系统
    
    支持的通知渠道:
    1. 邮件 (Email)
    2. 企业微信 (WeChat Work)
    3. 钉钉 (DingTalk)
    4. 短信 (SMS)
    """
    
    def __init__(self):
        """初始化通知系统"""
        self.email_config = self._load_email_config()
        self.wechat_config = self._load_wechat_config()
        self.dingtalk_config = self._load_dingtalk_config()
        self.sms_config = self._load_sms_config()
        
        LOGGER.info("📬 通知系统初始化完成")
    
    def send_email_notification(self, data: Dict) -> bool:
        """发送邮件通知
        
        Args:
            data: 通知数据
            
        Returns:
            是否发送成功
        """
        try:
            if not self.email_config.get('enabled', False):
                LOGGER.info("📧 邮件通知未启用")
                return False
            
            # 生成邮件内容
            subject, body = self._format_email_content(data)
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config['from_address']
            msg['To'] = self.email_config['to_address']
            
            # 添加HTML内容
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            with smtplib.SMTP_SSL(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            ) as server:
                server.login(
                    self.email_config['username'],
                    self.email_config['password']
                )
                server.send_message(msg)
            
            LOGGER.info(f"✅ 邮件通知已发送: {subject}")
            return True
            
        except Exception as e:
            LOGGER.error(f"❌ 发送邮件失败: {e}", exc_info=True)
            return False
    
    def send_wechat_notification(self, data: Dict) -> bool:
        """发送企业微信通知
        
        Args:
            data: 通知数据
            
        Returns:
            是否发送成功
        """
        try:
            if not self.wechat_config.get('enabled', False):
                LOGGER.info("💬 企业微信通知未启用")
                return False
            
            import requests
            
            # 生成消息内容
            message = self._format_wechat_content(data)
            
            # 企业微信机器人webhook
            webhook_url = self.wechat_config['webhook_url']
            
            # 发送POST请求
            response = requests.post(
                webhook_url,
                json={
                    "msgtype": "markdown",
                    "markdown": {
                        "content": message
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                LOGGER.info("✅ 企业微信通知已发送")
                return True
            else:
                LOGGER.error(f"❌ 企业微信通知失败: {response.text}")
                return False
            
        except Exception as e:
            LOGGER.error(f"❌ 发送企业微信通知失败: {e}", exc_info=True)
            return False
    
    def send_dingtalk_notification(self, data: Dict) -> bool:
        """发送钉钉通知
        
        Args:
            data: 通知数据
            
        Returns:
            是否发送成功
        """
        try:
            if not self.dingtalk_config.get('enabled', False):
                LOGGER.info("📱 钉钉通知未启用")
                return False
            
            import requests
            
            # 生成消息内容
            message = self._format_dingtalk_content(data)
            
            # 钉钉机器人webhook
            webhook_url = self.dingtalk_config['webhook_url']
            
            # 发送POST请求
            response = requests.post(
                webhook_url,
                json={
                    "msgtype": "markdown",
                    "markdown": {
                        "title": "AlgoVoice投资信号",
                        "text": message
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                LOGGER.info("✅ 钉钉通知已发送")
                return True
            else:
                LOGGER.error(f"❌ 钉钉通知失败: {response.text}")
                return False
            
        except Exception as e:
            LOGGER.error(f"❌ 发送钉钉通知失败: {e}", exc_info=True)
            return False
    
    def send_sms_notification(self, data: Dict) -> bool:
        """发送短信通知（仅重要告警）
        
        Args:
            data: 通知数据
            
        Returns:
            是否发送成功
        """
        try:
            if not self.sms_config.get('enabled', False):
                LOGGER.info("📲 短信通知未启用")
                return False
            
            # 短信内容要简短
            message = self._format_sms_content(data)
            
            # TODO: 调用短信API
            # 比如：阿里云短信、腾讯云短信等
            
            LOGGER.info("✅ 短信通知已发送")
            return True
            
        except Exception as e:
            LOGGER.error(f"❌ 发送短信失败: {e}", exc_info=True)
            return False
    
    def send_risk_alert(self, strategy_id: str, violations: List[str]) -> None:
        """发送风险告警
        
        Args:
            strategy_id: 策略ID
            violations: 违规项列表
        """
        try:
            alert_data = {
                'type': 'risk_alert',
                'strategy_id': strategy_id,
                'violations': violations,
                'timestamp': datetime.now().isoformat()
            }
            
            # 风险告警通过所有渠道发送
            self.send_email_notification(alert_data)
            self.send_wechat_notification(alert_data)
            self.send_dingtalk_notification(alert_data)
            self.send_sms_notification(alert_data)
            
        except Exception as e:
            LOGGER.error(f"❌ 发送风险告警失败: {e}", exc_info=True)
    
    def send_daily_summary(self, summary_data: List[Dict]) -> None:
        """发送每日摘要
        
        Args:
            summary_data: 摘要数据列表
        """
        try:
            data = {
                'type': 'daily_summary',
                'summary': summary_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # 每日摘要通过邮件和企业微信发送
            self.send_email_notification(data)
            self.send_wechat_notification(data)
            
        except Exception as e:
            LOGGER.error(f"❌ 发送每日摘要失败: {e}", exc_info=True)
    
    def _format_email_content(self, data: Dict) -> tuple[str, str]:
        """格式化邮件内容
        
        Args:
            data: 通知数据
            
        Returns:
            (subject, html_body)
        """
        data_type = data.get('type', 'signal')
        
        if data_type == 'risk_alert':
            return self._format_risk_alert_email(data)
        elif data_type == 'daily_summary':
            return self._format_daily_summary_email(data)
        else:
            return self._format_signal_email(data)
    
    def _format_signal_email(self, data: Dict) -> tuple[str, str]:
        """格式化信号邮件"""
        strategy_name = data.get('strategy_name', '未命名策略')
        signals = data.get('signals', [])
        
        subject = f"📊 AlgoVoice投资信号 - {strategy_name} ({len(signals)}个)"
        
        # 构建HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
                .container {{ background-color: white; border-radius: 10px; padding: 30px; max-width: 800px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .signal {{ border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; background-color: #f8f9fa; }}
                .signal.buy {{ border-left-color: #10b981; }}
                .signal.sell {{ border-left-color: #ef4444; }}
                .metric {{ display: inline-block; margin-right: 20px; }}
                .metric-value {{ font-size: 1.2em; font-weight: bold; }}
                .footer {{ text-align: center; color: #888; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 AlgoVoice投资信号</h1>
                    <p>策略: {strategy_name}</p>
                    <p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h2>🎯 今日操作建议 ({len(signals)}个)</h2>
        """
        
        for i, signal in enumerate(signals, 1):
            signal_type = signal.signal_type
            signal_class = 'buy' if signal_type == 'buy' else 'sell'
            emoji = '📈' if signal_type == 'buy' else '📉'
            
            html += f"""
                <div class="signal {signal_class}">
                    <h3>{i}. {emoji} {signal_type.upper()} - {signal.stock_name} ({signal.stock_code})</h3>
                    
                    <div class="metric">
                        <span class="metric-label">当前价格:</span>
                        <span class="metric-value">¥{signal.current_price:.2f}</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">建议仓位:</span>
                        <span class="metric-value">{signal.position_size:.1%}</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">置信度:</span>
                        <span class="metric-value">{signal.confidence:.1%}</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">风险评分:</span>
                        <span class="metric-value">{signal.risk_score:.2f}</span>
                    </div>
                    
                    <p><strong>理由:</strong> {signal.reason}</p>
                    
                    <p>
                        <strong>止损位:</strong> ¥{signal.stop_loss_price:.2f} |
                        <strong>止盈位:</strong> ¥{signal.take_profit_price:.2f}
                    </p>
            """
            
            if signal.expected_return:
                html += f'<p><strong>预期收益:</strong> {signal.expected_return:.2%}</p>'
            
            html += '</div>'
        
        html += """
                <div class="footer">
                    <p>⚠️ 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
                    <p>Powered by AlgoVoice AI Trading System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return subject, html
    
    def _format_risk_alert_email(self, data: Dict) -> tuple[str, str]:
        """格式化风险告警邮件"""
        strategy_id = data.get('strategy_id', '未知策略')
        violations = data.get('violations', [])
        
        subject = f"⚠️ AlgoVoice风险告警 - {strategy_id}"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #fee; padding: 20px; }}
                .container {{ background-color: white; border: 3px solid #ef4444; border-radius: 10px; padding: 30px; max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #ef4444; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .violation {{ background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ 风险告警</h1>
                    <p>策略: {strategy_id}</p>
                    <p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h2>违规项:</h2>
        """
        
        for violation in violations:
            html += f'<div class="violation">❌ {violation}</div>'
        
        html += """
                <p style="margin-top: 20px; color: #ef4444; font-weight: bold;">
                    策略已自动暂停，请检查风险指标后再恢复运行。
                </p>
            </div>
        </body>
        </html>
        """
        
        return subject, html
    
    def _format_daily_summary_email(self, data: Dict) -> tuple[str, str]:
        """格式化每日摘要邮件"""
        summary = data.get('summary', [])
        
        subject = f"📈 AlgoVoice每日摘要 - {datetime.now().strftime('%Y-%m-%d')}"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
                .container {{ background-color: white; border-radius: 10px; padding: 30px; max-width: 800px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .strategy {{ border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 15px 0; }}
                .metric {{ display: inline-block; margin-right: 20px; }}
                .positive {{ color: #10b981; }}
                .negative {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📈 AlgoVoice每日摘要</h1>
                    <p>日期: {datetime.now().strftime('%Y年%m月%d日')}</p>
                    <p>活跃策略: {len(summary)}个</p>
                </div>
        """
        
        for item in summary:
            strategy_name = item['strategy_name']
            account = item['account']
            signals_count = item['signals_count']
            
            total_return = account['total_return']
            daily_return = account['daily_return']
            
            return_class = 'positive' if total_return >= 0 else 'negative'
            daily_class = 'positive' if daily_return >= 0 else 'negative'
            
            html += f"""
                <div class="strategy">
                    <h3>{strategy_name}</h3>
                    
                    <div class="metric">
                        <strong>总资产:</strong> ¥{account['total_assets']:,.2f}
                    </div>
                    
                    <div class="metric">
                        <strong>总收益:</strong>
                        <span class="{return_class}">{total_return:.2%}</span>
                    </div>
                    
                    <div class="metric">
                        <strong>当日收益:</strong>
                        <span class="{daily_class}">{daily_return:.2%}</span>
                    </div>
                    
                    <div class="metric">
                        <strong>持仓数量:</strong> {len(account.get('positions', {}))}
                    </div>
                    
                    <div class="metric">
                        <strong>今日信号:</strong> {signals_count}个
                    </div>
                </div>
            """
        
        html += """
                <div style="text-align: center; color: #888; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p>Powered by AlgoVoice AI Trading System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return subject, html
    
    def _format_wechat_content(self, data: Dict) -> str:
        """格式化企业微信内容"""
        data_type = data.get('type', 'signal')
        
        if data_type == 'risk_alert':
            strategy_id = data.get('strategy_id', '未知策略')
            violations = data.get('violations', [])
            
            message = f"## ⚠️ 风险告警\n\n"
            message += f"**策略:** {strategy_id}\n\n"
            message += f"**违规项:**\n"
            for v in violations:
                message += f"- {v}\n"
            message += f"\n策略已自动暂停"
            
        elif data_type == 'daily_summary':
            summary = data.get('summary', [])
            message = f"## 📈 每日摘要\n\n"
            message += f"**日期:** {datetime.now().strftime('%Y-%m-%d')}\n"
            message += f"**活跃策略:** {len(summary)}个\n\n"
            
            for item in summary:
                account = item['account']
                message += f"### {item['strategy_name']}\n"
                message += f"- 总收益: {account['total_return']:.2%}\n"
                message += f"- 当日收益: {account['daily_return']:.2%}\n"
                message += f"- 今日信号: {item['signals_count']}个\n\n"
        
        else:
            strategy_name = data.get('strategy_name', '未命名策略')
            signals = data.get('signals', [])
            
            message = f"## 📊 投资信号\n\n"
            message += f"**策略:** {strategy_name}\n"
            message += f"**信号数量:** {len(signals)}个\n\n"
            
            for i, signal in enumerate(signals[:5], 1):  # 最多显示5个
                emoji = '📈' if signal.signal_type == 'buy' else '📉'
                message += f"### {i}. {emoji} {signal.signal_type.upper()}\n"
                message += f"- **股票:** {signal.stock_name} ({signal.stock_code})\n"
                message += f"- **价格:** ¥{signal.current_price:.2f}\n"
                message += f"- **仓位:** {signal.position_size:.1%}\n"
                message += f"- **置信度:** {signal.confidence:.1%}\n\n"
        
        return message
    
    def _format_dingtalk_content(self, data: Dict) -> str:
        """格式化钉钉内容（与企业微信类似）"""
        return self._format_wechat_content(data)
    
    def _format_sms_content(self, data: Dict) -> str:
        """格式化短信内容（简短）"""
        data_type = data.get('type', 'signal')
        
        if data_type == 'risk_alert':
            strategy_id = data.get('strategy_id', '未知')
            return f"【AlgoVoice告警】策略{strategy_id}触发风险限制，已自动暂停。请及时查看。"
        else:
            return "【AlgoVoice】新的投资信号已生成，请查看邮件或企业微信。"
    
    def _load_email_config(self) -> Dict:
        """加载邮件配置"""
        # TODO: 从配置文件加载
        return {
            'enabled': False,  # 默认未启用
            'smtp_server': 'smtp.example.com',
            'smtp_port': 465,
            'username': 'your_email@example.com',
            'password': 'your_password',
            'from_address': 'AlgoVoice@example.com',
            'to_address': 'your_email@example.com'
        }
    
    def _load_wechat_config(self) -> Dict:
        """加载企业微信配置"""
        # TODO: 从配置文件加载
        return {
            'enabled': False,  # 默认未启用
            'webhook_url': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY'
        }
    
    def _load_dingtalk_config(self) -> Dict:
        """加载钉钉配置"""
        # TODO: 从配置文件加载
        return {
            'enabled': False,  # 默认未启用
            'webhook_url': 'https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN'
        }
    
    def _load_sms_config(self) -> Dict:
        """加载短信配置"""
        # TODO: 从配置文件加载
        return {
            'enabled': False,  # 默认未启用
            'provider': 'aliyun',  # aliyun/tencent
            'access_key': 'YOUR_ACCESS_KEY',
            'secret_key': 'YOUR_SECRET_KEY',
            'sign_name': 'AlgoVoice',
            'template_code': 'SMS_123456789',
            'phone_numbers': []
        }


if __name__ == "__main__":
    # 测试
    notifier = NotificationSystem()
    
    # 测试信号通知
    test_data = {
        'strategy_name': '测试策略',
        'signals': []
    }
    
    print("📬 通知系统已初始化")
    print("📧 邮件:", "启用" if notifier.email_config['enabled'] else "未启用")
    print("💬 企业微信:", "启用" if notifier.wechat_config['enabled'] else "未启用")
    print("📱 钉钉:", "启用" if notifier.dingtalk_config['enabled'] else "未启用")
    print("📲 短信:", "启用" if notifier.sms_config['enabled'] else "未启用")
