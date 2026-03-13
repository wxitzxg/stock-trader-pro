"""
Position Import Utilities - 持仓导入工具
支持 JSON/CSV/券商交割单格式解析
"""
import csv
import json
from typing import List, Dict
from datetime import datetime


def parse_json_file(file_path: str) -> List[Dict]:
    """
    解析 JSON 格式持仓文件

    Args:
        file_path: 文件路径

    Returns:
        标准化的持仓数据列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 支持两种格式：直接列表或包含 data 字段的对象
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "data" in data:
        return data["data"]
    elif isinstance(data, dict) and "positions" in data:
        return data["positions"]
    else:
        raise ValueError("JSON 格式不正确，应为列表或包含 'data'/'positions' 字段的对象")


def parse_csv_file(file_path: str) -> List[Dict]:
    """
    解析 CSV 格式持仓文件

    Args:
        file_path: 文件路径

    Returns:
        标准化的持仓数据列表
    """
    positions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 转换 CSV 字符串为适当类型
            row_data = {
                "stock_code": row.get("stock_code", row.get("代码", row.get("股票代码"))),
                "stock_name": row.get("stock_name", row.get("名称", row.get("股票名称"))),
                "quantity": int(row.get("quantity", row.get("数量", row.get("持仓数量", 0)))),
                "avg_cost": float(row.get("avg_cost", row.get("成本价", row.get("持仓成本", 0)))),
                "current_price": float(row.get("current_price", row.get("当前价", row.get("现价", row.get("最新价", 0))))),
                "purchase_date": row.get("purchase_date", row.get("建仓日期", row.get("买入日期"))),
                "notes": row.get("notes", row.get("备注"))
            }

            # 处理总成本（如果有）
            if "total_cost" in row or "总成本" in row:
                row_data["total_cost"] = float(row.get("total_cost", row.get("总成本", 0)))

            positions.append(row_data)

    return positions


def parse_broker_statement(
    file_path: str,
    broker: str = "auto"
) -> List[Dict]:
    """
    解析券商交割单

    支持的券商：
    - 华泰证券
    - 中信证券
    - 国泰君安
    - 东方财富
    - 华泰涨乐财富通

    Args:
        file_path: 文件路径（支持 CSV/XLSX）
        broker: 券商名称，"auto" 自动检测

    Returns:
        标准化的持仓数据列表
    """
    # 检测文件类型
    if file_path.endswith('.csv'):
        return _parse_broker_csv(file_path, broker)
    elif file_path.endswith(('.xlsx', '.xls')):
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            return _parse_broker_dataframe(df, broker)
        except ImportError:
            raise ImportError("解析 Excel 文件需要安装 pandas 和 openpyxl: pip install pandas openpyxl")
    else:
        raise ValueError("不支持的文件格式，仅支持 CSV 和 XLSX")


def _parse_broker_csv(file_path: str, broker: str = "auto") -> List[Dict]:
    """解析券商 CSV 交割单"""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return []

    # 自动检测券商
    if broker == "auto":
        broker = _detect_broker(rows[0])

    # 根据券商选择解析器
    parser = _get_broker_parser(broker)
    return parser(rows)


def _parse_broker_dataframe(df, broker: str = "auto") -> List[Dict]:
    """解析券商 Excel 交割单（DataFrame）"""
    if broker == "auto":
        broker = _detect_broker_from_df(df)

    parser = _get_broker_parser(broker)
    return parser(df.to_dict('records'))


def _detect_broker(row: Dict) -> str:
    """从 CSV 行检测券商"""
    # 检查列名特征
    columns = ''.join(row.keys())

    if '华泰' in columns or '涨乐' in columns:
        return 'huatai'
    elif '中信' in columns:
        return 'citic'
    elif '国泰君安' in columns or '君弘' in columns:
        return 'guotai'
    elif '东方财富' in columns or '东财' in columns:
        return 'eastmoney'
    else:
        # 默认使用通用解析器
        return 'generic'


def _detect_broker_from_df(df) -> str:
    """从 DataFrame 检测券商"""
    columns = ''.join(df.columns.tolist())

    if '华泰' in columns or '涨乐' in columns:
        return 'huatai'
    elif '中信' in columns:
        return 'citic'
    elif '国泰君安' in columns or '君弘' in columns:
        return 'guotai'
    elif '东方财富' in columns or '东财' in columns:
        return 'eastmoney'
    else:
        return 'generic'


def _get_broker_parser(broker: str):
    """获取券商对应的解析器"""
    parsers = {
        'huatai': _parse_huatai,
        'citic': _parse_citic,
        'guotai': _parse_guotai,
        'eastmoney': _parse_eastmoney,
        'generic': _parse_generic
    }
    return parsers.get(broker, _parse_generic)


def _parse_huatai(rows: List[Dict]) -> List[Dict]:
    """华泰证券交割单解析"""
    positions = []
    for row in rows:
        # 只统计持仓，不处理交易记录
        if '余额' in row or '当前余额' in row:
            try:
                quantity = int(row.get('余额', row.get('当前余额', 0)))
                if quantity <= 0:
                    continue

                avg_cost = float(row.get('成本价', row.get('摊薄成本价', 0)))
                current_price = float(row.get('最新价', row.get('当前价', 0)))

                positions.append({
                    "stock_code": row.get('证券代码', row.get('股票代码', '')),
                    "stock_name": row.get('证券简称', row.get('股票简称', '')),
                    "quantity": quantity,
                    "avg_cost": avg_cost,
                    "current_price": current_price if current_price > 0 else avg_cost,
                    "total_cost": float(row.get('成本金额', 0)) if row.get('成本金额') else None
                })
            except (ValueError, KeyError):
                continue

    return positions


def _parse_citic(rows: List[Dict]) -> List[Dict]:
    """中信证券交割单解析"""
    positions = []
    for row in rows:
        if '持仓数量' in row or '股份余额' in row:
            try:
                quantity = int(row.get('持仓数量', row.get('股份余额', 0)))
                if quantity <= 0:
                    continue

                avg_cost = float(row.get('持仓成本', row.get('成本价', 0)))
                current_price = float(row.get('最新价', row.get('市价', 0)))

                positions.append({
                    "stock_code": row.get('证券代码', ''),
                    "stock_name": row.get('证券名称', row.get('股票名称', '')),
                    "quantity": quantity,
                    "avg_cost": avg_cost,
                    "current_price": current_price if current_price > 0 else avg_cost
                })
            except (ValueError, KeyError):
                continue

    return positions


def _parse_guotai(rows: List[Dict]) -> List[Dict]:
    """国泰君安交割单解析"""
    positions = []
    for row in rows:
        if '可用数量' in row or '持仓数量' in row:
            try:
                quantity = int(row.get('可用数量', row.get('持仓数量', 0)))
                if quantity <= 0:
                    continue

                avg_cost = float(row.get('成本价', 0))
                current_price = float(row.get('当前价', row.get('市价', 0)))

                positions.append({
                    "stock_code": row.get('证券代码', ''),
                    "stock_name": row.get('证券名称', ''),
                    "quantity": quantity,
                    "avg_cost": avg_cost,
                    "current_price": current_price if current_price > 0 else avg_cost
                })
            except (ValueError, KeyError):
                continue

    return positions


def _parse_eastmoney(rows: List[Dict]) -> List[Dict]:
    """东方财富交割单解析"""
    positions = []
    for row in rows:
        if '持仓数量' in row or '可用数量' in row:
            try:
                quantity = int(row.get('持仓数量', row.get('可用数量', 0)))
                if quantity <= 0:
                    continue

                avg_cost = float(row.get('成本价', row.get('持仓成本', 0)))
                current_price = float(row.get('最新价', row.get('当前价', 0)))

                positions.append({
                    "stock_code": row.get('证券代码', ''),
                    "stock_name": row.get('证券名称', ''),
                    "quantity": quantity,
                    "avg_cost": avg_cost,
                    "current_price": current_price if current_price > 0 else avg_cost
                })
            except (ValueError, KeyError):
                continue

    return positions


def _parse_generic(rows: List[Dict]) -> List[Dict]:
    """
    通用解析器 - 尝试从任意 CSV 中提取持仓数据

    支持的列名变体：
    - 代码类：stock_code, 证券代码，股票代码，代码，symbol
    - 名称类：stock_name, 证券名称，股票名称，名称，name
    - 数量类：quantity, 持仓数量，可用数量，余额，数量
    - 成本类：avg_cost, 成本价，持仓成本，成本
    - 价格类：current_price, 当前价，最新价，市价，现价
    """
    positions = []

    # 列名映射表
    code_cols = ['stock_code', '证券代码', '股票代码', '代码', 'symbol', '证券编码']
    name_cols = ['stock_name', '证券名称', '股票名称', '名称', 'name', '简称']
    qty_cols = ['quantity', '持仓数量', '可用数量', '余额', '数量', '持股数', '股份余额']
    cost_cols = ['avg_cost', '成本价', '持仓成本', '成本', '买入均价', '摊薄成本价']
    price_cols = ['current_price', '当前价', '最新价', '市价', '现价', '股价']

    for row in rows:
        try:
            # 查找对应列
            stock_code = _find_column_value(row, code_cols)
            stock_name = _find_column_value(row, name_cols)
            quantity = _find_column_value(row, qty_cols, default=0)
            avg_cost = _find_column_value(row, cost_cols, default=0)
            current_price = _find_column_value(row, price_cols, default=avg_cost)

            # 转换类型
            quantity = int(float(quantity))
            avg_cost = float(avg_cost)
            current_price = float(current_price) if current_price else avg_cost

            if quantity <= 0 or not stock_code:
                continue

            position_data = {
                "stock_code": str(stock_code),
                "stock_name": str(stock_name) if stock_name else stock_code,
                "quantity": quantity,
                "avg_cost": avg_cost,
                "current_price": current_price
            }

            # 查找总成本
            total_cost = _find_column_value(row, ['total_cost', '总成本', '成本金额', '持有金额'])
            if total_cost:
                position_data["total_cost"] = float(total_cost)

            positions.append(position_data)

        except (ValueError, KeyError, TypeError):
            # 跳过无法解析的行
            continue

    return positions


def _find_column_value(row: Dict, column_names: List[str], default=None):
    """
    在 row 中查找列名（支持多个可能的列名）

    Args:
        row: 数据行
        column_names: 可能的列名列表
        default: 默认值

    Returns:
        找到的值或默认值
    """
    for col in column_names:
        if col in row and row[col]:
            return row[col]
    return default


# 导出函数
__all__ = [
    'parse_json_file',
    'parse_csv_file',
    'parse_broker_statement',
]
