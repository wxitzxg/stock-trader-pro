# 📊 A 股智能监控预警报告

> **生成时间**: {{report_time}}
> **市场状态**: {{market_status}}
> **监控模式**: 仅交易日交易时段预警

---

## 📈 汇总统计

| 项目 | 持仓股 | 收藏股 |
|------|--------|--------|
| 数量 | {{position_count}} 只 | {{watchlist_count}} 只 |
| 总市值 | {{total_value}} | - |
| 总成本 | {{total_cost}} | - |
| 浮动盈亏 | {{total_profit}} ({{profit_rate}}) | - |
| 预警数 | {{position_alerts}} 条 | {{watchlist_alerts}} 条 |

---

## 🚨 预警信息汇总

{{alerts_section}}

---

## 📋 预警规则详情

### 已触发规则

{{triggered_rules_table}}

### 正常状态规则（前 10 条）

{{normal_rules_table}}

### 规则阈值说明

| 规则类型 | 规则名称 | 默认阈值 | 说明 |
|----------|----------|----------|------|
| 成本规则 | cost_above | ≥15% | 盈利超过 15% 提醒止盈 |
| 成本规则 | cost_below | ≤-12% | 亏损超过 12% 警惕止损 |
| 价格规则 | pct_up | ≥4% | 日内大涨超过 4% |
| 价格规则 | pct_down | ≤-4% | 日内大跌超过 4% |
| 成交量规则 | volume_surge | ≥2 倍 | 成交量是 5 日均量 2 倍以上 |
| 成交量规则 | volume_shrink | ≤0.5 倍 | 成交量是 5 日均量 50% 以下 |
| 技术指标 | ma_golden | - | MA5 上穿 MA10（金叉） |
| 技术指标 | ma_death | - | MA5 下穿 MA10（死叉） |
| 技术指标 | rsi_high | >70 | RSI 超买区域 |
| 技术指标 | rsi_low | <30 | RSI 超卖区域 |

---

## 💼 持仓股监控

{{positions_table}}

{{positions_detail}}

---

## 🏷️ 收藏股监控

{{watchlist_table}}

{{watchlist_detail}}

---

## ⚠️ 风险提示

{{risk_tips}}

---

## 📅 下次监控时间

- **下午开盘**: 13:00（如当前在午休）
- **明日开盘**: 次日 9:30（如已收盘）
- **下周一开盘**: 如当前为周末或节假日

---

*本报告由 Technical Indicators Pro v2.4 自动生成*
*监控策略：仅 A 股交易日 9:30-11:30 和 13:00-15:00 执行预警*
