"""
配置管理模块 - 统一配置中心
stock-trader-pro 项目统一配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# ========== 数据库配置 ==========
DATABASE_PATH = os.getenv(
    "INVEST_DB_PATH",
    BASE_DIR / "storage" / "investment.db"
)

# ========== AKShare 配置 ==========
AKSHARE_TIMEOUT = 30  # 请求超时时间（秒）
AKSHARE_SEARCH_LIMIT = 20  # 搜索结果数量
AKSHARE_EXPORT_DAYS_DEFAULT = 60  # 导出默认天数

# ========== K 线缓存配置 ==========
KLINE_CACHE_ENABLED = True       # 是否启用数据库缓存
KLINE_DEFAULT_DAYS = 250         # 默认初始化天数
KLINE_DAILY_UPDATE_TIME = "00:00"  # 每日更新时间

# ========== 波段策略参数 ==========
STRATEGY_PARAMS = {
    # 均线参数
    "ma_short": 5,       # 短期均线
    "ma_mid": 20,        # 中期均线
    "ma_long": 50,       # 长期均线
    "ma_ema_200": 200,   # EMA200 牛熊分界

    # RSI 参数
    "rsi_period": 14,    # RSI 周期
    "rsi_overbought": 70,  # 超买阈值
    "rsi_oversold": 30,    # 超卖阈值

    # 布林带参数
    "boll_period": 20,   # 布林带周期
    "boll_std": 2.0,     # 布林带标准差

    # MACD 参数
    "macd_fast": 12,     # MACD 快线
    "macd_slow": 26,     # MACD 慢线
    "macd_signal": 9,    # MACD 信号线

    # VCP 参数
    "vcp_min_drops": 2,        # 最少回调次数
    "vcp_max_drops": 4,        # 最多回调次数
    "vcp_min_contraction": 0.5, # 最小收缩比例 (50%)

    # 神奇九转参数
    "td_period": 9,      # 九转周期
    "td_compare_period": 4,  # 比较周期

    # ZigZag 参数
    "zigzag_threshold": 0.05,  # ZigZag 阈值 (5%)
}

# ========== 信号置信度阈值 ==========
SIGNAL_THRESHOLD = {
    "high": 80,      # 高置信度 (S 级)
    "medium": 65,    # 中置信度 (A 级)
    "low": 40,       # 低置信度 (B 级)
}

# ========== 五维评分权重 ==========
FIVE_DIMENSION_WEIGHTS = {
    "D1_trend": 20,    # 趋势维 - 必要门槛
    "D2_pattern": 30,  # 形态维 - 核心灵魂
    "D3_position": 20, # 位置维 - 重要辅助
    "D4_momentum": 10, # 动能维 - 关键确认
    "D5_trigger": 20,  # 触发维 - 执行信号
}

# ========== 决策阈值 ==========
DECISION_THRESHOLD = {
    "strong_buy": 85,   # S 级 - 满仓 20%
    "buy": 65,          # A 级 - 半仓 10%
    "hold": 40,         # B 级 - 观察
}

# ========== 仓位管理参数 ==========
POSITION_PARAMS = {
    "max_single_position": 0.20,  # 单只股票最大仓位 20%
    "kelly_factor": 0.5,          # Kelly 系数 (保守版)
    "min_position": 0.05,         # 最小仓位 5%
}

# ========== 涨跌幅预警阈值 ==========
PRICE_ALERT_THRESHOLD = {
    "rise": 5.0,     # 涨幅超过 5%
    "fall": -5.0,    # 跌幅超过 5%
}


# ========== 修正后的交易费用配置 (基于实盘交割单反推) ==========
TRADING_FEES = {
    # 1. 印花税：卖出时收取 0.05% (0.0005)
    # 依据：乐普医疗卖出 25245 元，扣除 12.62 元 -> 12.62/25245 ≈ 0.0004999
    "stamp_duty": 0.0005,        
    
    # 2. 交易所规费 (即交割单中的"其他费用")
    # 依据：
    # 乐普: 1.61 / 25245 ≈ 0.0000637
    # 药明: 1.30 / 24000 ≈ 0.0000541
    # 平均约为 万分之 0.6 (0.00006)。默认值 0.00002 偏低。
    "exchange_fee": 0.00006,     
    
    # 3. 券商佣金率
    # 依据：
    # 乐普: 3.39 / 25245 ≈ 0.000134 (万 1.34)
    # 药明: 3.70 / 24000 ≈ 0.000154 (万 1.54)
    # 考虑到可能的四舍五入，设定为 万分之 1.5 (0.00015) 最为安全准确。
    "broker_commission": 0.00015, 

    # 4. 最低佣金限制
    # 依据：您的两笔交易佣金均小于 5 元 (3.39 和 3.70)，且按实际金额收取，未被强制上调至 5 元。
    # 结论：您的账户极可能已取消“最低5元”限制，或阈值极低。
    # 建议设为 0，以真实反映您的小额交易成本优势。
    "min_commission": 0.0
}
# ========== 止损参数 ==========
STOP_LOSS_PARAMS = {
    "vcp_breakout": {
        "initial_stop_pct": 0.03,  # 枢轴点下方 3%
        "trail_start_pct": 0.10,   # 获利 10% 后启动移动止损
        "trail_step_pct": 0.02,    # 每涨 5% 上移 2%
    },
    "td_golden_pit": {
        "initial_stop_pct": 0.02,  # 低九期间最低价下方 2%
        "break_even_target": 0.10, # 获利 10% 后移至成本价
    }
}

# ========== 监控预警配置 ==========
MONITOR_CONFIG = {
    # 预警规则默认值
    "cost_pct_above": 15.0,    # 盈利 15% 预警
    "cost_pct_below": -12.0,   # 亏损 12% 预警
    "change_pct_above": 4.0,   # 日内大涨
    "change_pct_below": -4.0,  # 日内大跌
    "volume_surge": 2.0,       # 放量倍数

    # 智能频率（秒）- 支持自定义配置
    "interval_market": 300,     # 交易时间 5 分钟
    "interval_lunch": 600,      # 午休 10 分钟
    "interval_after_hours": 1800,  # 收盘后 30 分钟
    "interval_night": 3600,     # 凌晨 1 小时
    "interval_weekend": 3600,   # 周末 1 小时

    # 价格更新配置
    "price_update_enabled": True,           # 是否启用价格更新
    "price_update_check_interval": 60,      # 检查间隔（秒）- 多久检查一次是否该更新
    "price_update_interval_market": 300,    # 交易时段更新频率（秒）- 每 5 分钟更新一次
}

# ========== 报告输出配置 ==========
REPORT_CONFIG = {
    # 默认输出位置
    "default_output_dir": "./monitor_reports",  # 默认报告输出目录
    "output_format": "markdown",  # 输出格式：markdown/html/json

    # 模版文件配置
    "template_file": str(BASE_DIR / "config" / "monitor_report_template.md"),  # 自定义模版文件路径

    # 报告内容配置
    "include_summary": True,       # 包含汇总统计
    "include_alerts": True,        # 包含预警信息
    "include_positions": True,     # 包含持仓股详情
    "include_watchlist": True,     # 包含收藏股详情
    "include_risk_tips": True,     # 包含风险提示
    "include_rule_details": True,  # 包含预警规则详情

    # 预警规则详情配置
    "rule_details": {
        "cost_rule": True,         # 成本百分比规则
        "price_rule": True,        # 价格涨跌幅规则
        "volume_rule": True,       # 成交量规则
        "technical_rule": True,    # 技术指标规则
        "trailing_stop": True,     # 动态止盈止损
    }
}

# ========== 日志配置 ==========
LOG_LEVEL = os.getenv("INVEST_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "storage" / "stock-trader.log"
