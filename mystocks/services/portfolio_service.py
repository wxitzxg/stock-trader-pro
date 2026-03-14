"""
PortfolioService - 持仓业务逻辑
"""
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP

from mystocks.models.position import Position, PositionLot
from mystocks.models.transaction import Transaction
from mystocks.storage.repositories.position_repo import PositionRepository
from mystocks.storage.repositories.transaction_repo import TransactionRepository
from mystocks.storage.repositories.account_repo import AccountRepository
from config.settings import TRADING_FEES
from stockquery import get_default_service

# 小数精度常量
DECIMAL_PRECISION = '0.0001'


class InitMode(str, Enum):
    """持仓初始化模式"""
    OVERWRITE = "overwrite"  # 覆盖原有持仓
    ADD = "add"  # 累加到原有持仓


class PortfolioService:
    """持仓业务逻辑"""

    def __init__(self, session):
        """
        初始化持仓服务

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self._position_repo = PositionRepository(session)
        self._transaction_repo = TransactionRepository(session)
        self._account_repo = AccountRepository(session)

    def _get_default_account(self):
        """获取默认账户"""
        return self._account_repo.get_or_create_default()

    def buy(
        self,
        stock_code: str,
        stock_name: str,
        quantity: int,
        price: float,
        commission: float = 0.0,
        notes: str = None,
        account_id: int = None
    ) -> Position:
        """
        买入股票

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            quantity: 股数
            price: 成交价
            commission: 手续费
            notes: 备注
            account_id: 账户 ID，为 None 时使用默认账户

        Returns:
            持仓对象
        """
        if quantity <= 0:
            raise ValueError("买入数量必须为正数")
        if price <= 0:
            raise ValueError("买入价格必须为正数")

        total_amount = quantity * price
        total_cost = total_amount + commission

        # 获取账户并扣除现金
        account = self._get_default_account() if account_id is None else self._account_repo.get(account_id)
        if account is None:
            raise ValueError(f"账户不存在：{account_id}")

        # 使用账户域的 withdraw 方法扣除现金
        try:
            account.withdraw(total_cost)
        except ValueError as e:
            raise ValueError(f"现金余额不足：{e}")

        # 检查是否已有持仓
        position = self._position_repo.get(stock_code)

        if position:
            # 更新持仓成本和数量
            old_total_cost = position.avg_cost * position.quantity
            new_quantity = position.quantity + quantity
            new_total_cost = old_total_cost + total_cost
            position.avg_cost = new_total_cost / new_quantity if new_quantity > 0 else 0
            position.quantity = new_quantity
            position.total_cost += total_cost
            self._position_repo.update(position)
        else:
            # 新建持仓
            avg_cost_with_commission = total_cost / quantity
            position = Position(
                stock_code=stock_code,
                stock_name=stock_name,
                quantity=quantity,
                avg_cost=avg_cost_with_commission,
                current_price=price,
                total_cost=total_cost
            )
            self._position_repo.add(position)

        # 创建持仓批次
        lot = PositionLot(
            position_id=position.id,
            stock_code=stock_code,
            quantity=quantity,
            cost_price=price,
            commission=commission,
            total_cost=total_cost,
            remaining_quantity=quantity
        )
        self._position_repo.add_lot(lot)

        # 记录交易
        transaction = Transaction(
            stock_code=stock_code,
            stock_name=stock_name,
            operation="buy",
            quantity=quantity,
            price=price,
            total_amount=total_amount,
            commission=commission,
            notes=notes,
            position_id=position.id,
            lot_id=lot.id
        )
        self._transaction_repo.add(transaction)

        # 提交账户变更
        self._account_repo.update(account)

        return position

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: float,
        commission: float = 0.0,
        notes: str = None,
        account_id: int = None
    ) -> Optional[Position]:
        """
        卖出股票（FIFO 成本计算）

        Args:
            stock_code: 股票代码
            quantity: 卖出股数
            price: 成交价
            commission: 手续费
            notes: 备注
            account_id: 账户 ID，为 None 时使用默认账户

        Returns:
            更新后的持仓对象，或 None（清仓）
        """
        if quantity <= 0:
            raise ValueError("卖出数量必须为正数")
        if price <= 0:
            raise ValueError("卖出价格必须为正数")

        position = self._position_repo.get(stock_code)

        if not position:
            return None

        if position.quantity < quantity:
            return None

        # FIFO 扣减持仓批次
        lots = self._position_repo.get_lots(stock_code)

        remaining_to_sell = quantity
        total_realized_pnl = 0.0

        for lot in lots:
            if remaining_to_sell <= 0:
                break

            sell_from_lot = min(lot.remaining_quantity, remaining_to_sell)

            # 计算该批次的实现盈亏
            cost_basis = lot.cost_price * sell_from_lot
            proceeds = sell_from_lot * price
            lot_commission_ratio = sell_from_lot / quantity
            realized_pnl = proceeds - cost_basis - (commission * lot_commission_ratio)
            total_realized_pnl += realized_pnl

            # 更新批次剩余数量
            lot.remaining_quantity -= sell_from_lot
            self._position_repo.update_lot(lot)

            remaining_to_sell -= sell_from_lot

        # 更新持仓
        position.quantity -= quantity
        position.realized_profit += total_realized_pnl

        if position.quantity == 0:
            # 清仓
            self._position_repo.delete(position)
            position = None
        else:
            self._position_repo.update(position)

        # 记录交易
        transaction = Transaction(
            stock_code=stock_code,
            stock_name=position.stock_name if position else stock_code,
            operation="sell",
            quantity=quantity,
            price=price,
            total_amount=quantity * price - commission,
            commission=commission,
            realized_pnl=total_realized_pnl,
            notes=notes,
            position_id=position.id if position else None
        )
        self._transaction_repo.add(transaction)

        # 更新账户：增加现金和已实现盈亏
        account = self._get_default_account() if account_id is None else self._account_repo.get(account_id)
        if account:
            # 增加现金（卖出所得 - 手续费）
            cash_proceeds = quantity * price - commission
            account.credit_cash(cash_proceeds)
            # 累计已实现盈亏
            account.add_realized_pnl(total_realized_pnl)
            self._account_repo.update(account)

        return position

    def get_position(self, stock_code: str) -> Optional[Position]:
        """获取单个持仓"""
        return self._position_repo.get(stock_code)

    def get_all_positions(self) -> List[Position]:
        """获取所有持仓"""
        return self._position_repo.get_all()

    def get_transactions(self, stock_code: str = None, limit: int = 50) -> List[Transaction]:
        """获取交易历史"""
        if stock_code:
            return self._transaction_repo.get_by_stock(stock_code, limit)
        return self._transaction_repo.get_all(limit)

    def calculate_commission(self, amount: float, operation: str = "buy") -> float:
        """
        计算交易手续费

        Args:
            amount: 交易金额
            operation: 操作类型（buy/sell）

        Returns:
            手续费金额
        """
        fees = TRADING_FEES

        # 印花税（仅卖出收取）
        stamp_duty = amount * fees["stamp_duty"] if operation == "sell" else 0

        # 交易所规费
        exchange_fee = amount * fees["exchange_fee"]

        # 券商佣金
        broker_commission = max(
            amount * fees["broker_commission"],
            fees["min_commission"]
        )

        return stamp_duty + exchange_fee + broker_commission

    def initialize_position(
        self,
        stock_code: str,
        quantity: int,
        avg_cost: float,
        current_price: float = None,
        stock_name: str = None,
        total_cost: float = None,
        purchase_date: str = None,
        mode: InitMode = InitMode.OVERWRITE,
        notes: str = None
    ) -> Position:
        """
        初始化持仓（用于首次导入已有持仓）

        与 buy() 的区别：
        - 不创建 Transaction 记录（因为不是实际交易，是历史持仓导入）
        - 支持覆盖或累加模式
        - 直接设置 avg_cost 和 current_price
        - 自动获取股票信息（当 current_price 或 stock_name 为 None 时）

        Args:
            stock_code: 股票代码（必需）
            quantity: 持仓数量（必需）
            avg_cost: 成本价，可为负数，精度为 4 位小数（必需）
            current_price: 当前价，为 None 时自动从 API 获取（可选）
            stock_name: 股票名称，为 None 时自动从 API 获取（可选）
            total_cost: 总成本（可选，默认 quantity * abs(avg_cost)）
            purchase_date: 建仓日期（可选，默认今天）
            mode: 初始化模式（overwrite=覆盖，add=累加）
            notes: 备注

        Returns:
            创建的持仓对象

        股票信息获取逻辑：
            - 当 current_price 或 stock_name 为 None 时
            - 调用 UnifiedStockQueryService.get_quote(stock_code) 获取
            - 数据源优先级：新浪财经 → AKShare（备用）
        """
        # 自动获取股票信息
        if current_price is None or stock_name is None:
            stock_query_service = get_default_service(timeout=10)
            quote = stock_query_service.get_quote(stock_code)

            if not quote:
                raise ValueError(f"无法获取股票 {stock_code} 的实时行情")

            # 使用 API 返回的数据填充缺失字段
            if stock_name is None:
                stock_name = quote.get('name', stock_code)
            if current_price is None:
                current_price = quote.get('price', 0)

                if current_price <= 0:
                    raise ValueError(f"股票 {stock_code} 的当前价格无效")

        # 精度控制：四舍五入到 4 位小数
        avg_cost = self._round_to_4_decimals(avg_cost)
        current_price = self._round_to_4_decimals(current_price)

        # 计算总成本
        if total_cost is None:
            total_cost = quantity * abs(avg_cost)

        # 验证（允许负成本）
        if quantity <= 0:
            raise ValueError("持仓数量必须为正数")
        if avg_cost == 0:
            raise ValueError("成本价不能为 0")

        # 解析建仓日期
        if purchase_date:
            try:
                purchase_dt = datetime.strptime(purchase_date, "%Y-%m-%d")
            except ValueError:
                purchase_dt = datetime.now()
        else:
            purchase_dt = datetime.now()

        # 检查是否已有持仓
        position = self._position_repo.get(stock_code)

        if position:
            if mode == InitMode.OVERWRITE:
                # 覆盖模式：删除原有持仓和批次，重新创建
                # 先删除所有批次
                lots = self._position_repo.get_lots(stock_code)
                for lot in lots:
                    self.session.delete(lot)
                self.session.commit()

                # 更新持仓
                position.quantity = quantity
                position.avg_cost = avg_cost
                position.current_price = current_price
                position.total_cost = total_cost
                # 负成本盈亏计算
                position.profit_loss, position.profit_rate = self._calculate_profit_loss(
                    avg_cost, current_price, quantity
                )
                self._position_repo.update(position)
            else:
                # 累加模式：类似 buy() 逻辑
                old_total_cost = position.avg_cost * position.quantity
                new_quantity = position.quantity + quantity
                new_total_cost = old_total_cost + total_cost
                position.avg_cost = new_total_cost / new_quantity if new_quantity > 0 else 0
                position.quantity = new_quantity
                position.total_cost += total_cost
                position.current_price = current_price  # 更新当前价
                # 负成本盈亏计算
                position.profit_loss, position.profit_rate = self._calculate_profit_loss(
                    position.avg_cost, current_price, new_quantity
                )
                self._position_repo.update(position)
        else:
            # 新建持仓
            profit_loss, profit_rate = self._calculate_profit_loss(avg_cost, current_price, quantity)
            position = Position(
                stock_code=stock_code,
                stock_name=stock_name,
                quantity=quantity,
                avg_cost=avg_cost,
                current_price=current_price,
                total_cost=total_cost,
                profit_loss=profit_loss,
                profit_rate=profit_rate
            )
            self._position_repo.add(position)

        # 创建持仓批次
        lot = PositionLot(
            position_id=position.id,
            stock_code=stock_code,
            quantity=quantity,
            cost_price=avg_cost,
            commission=0.0,  # 初始化时不记录手续费
            total_cost=total_cost,
            remaining_quantity=quantity,
            purchase_date=purchase_dt
        )
        self._position_repo.add_lot(lot)

        return position

    def _round_to_4_decimals(self, value: float) -> float:
        """四舍五入到 4 位小数"""
        return float(Decimal(str(value)).quantize(Decimal(DECIMAL_PRECISION), rounding=ROUND_HALF_UP))

    def _calculate_profit_loss(self, avg_cost: float, current_price: float, quantity: int) -> tuple:
        """
        计算盈亏金额和盈亏率

        负成本规则：
        - 当 avg_cost < 0 时，不计算盈亏率（返回 0 作为占位符）
        - 盈利金额 = (|成本价 | + 现价) × 数量

        Args:
            avg_cost: 成本价（可为负数）
            current_price: 当前价
            quantity: 持仓数量

        Returns:
            (profit_loss, profit_rate) 元组
            - profit_loss: 盈亏金额（4 位小数精度）
            - profit_rate: 盈亏率（负成本时为 0）
        """
        if avg_cost < 0:
            # 负成本：盈利 = (|成本 | + 现价) × 数量
            profit_loss = (abs(avg_cost) + current_price) * quantity
            profit_rate = 0.0  # 负成本时盈亏率无意义，用 0 占位
        else:
            # 正成本：标准公式
            profit_loss = (current_price - avg_cost) * quantity
            profit_rate = ((current_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0

        # 精度控制
        profit_loss = self._round_to_4_decimals(profit_loss)
        if profit_rate is not None:
            profit_rate = self._round_to_4_decimals(profit_rate)

        return profit_loss, profit_rate

    def initialize_positions_batch(
        self,
        positions_data: List[Dict],
        mode: InitMode = InitMode.OVERWRITE
    ) -> List[Position]:
        """
        批量初始化持仓

        Args:
            positions_data: 持仓数据列表，每项包含:
                - stock_code (必需)
                - stock_name (必需)
                - quantity (必需)
                - avg_cost (必需)
                - current_price (必需)
                - total_cost (可选)
                - purchase_date (可选，格式：YYYY-MM-DD)
                - notes (可选)
            mode: 初始化模式（overwrite=覆盖，add=累加）

        Returns:
            List[Position]: 创建的持仓列表
        """
        positions = []
        for data in positions_data:
            try:
                position = self.initialize_position(
                    stock_code=data.get("stock_code"),
                    stock_name=data.get("stock_name", data.get("stock_code")),
                    quantity=data.get("quantity"),
                    avg_cost=data.get("avg_cost"),
                    current_price=data.get("current_price", data.get("avg_cost")),
                    total_cost=data.get("total_cost"),
                    purchase_date=data.get("purchase_date"),
                    mode=mode,
                    notes=data.get("notes")
                )
                positions.append(position)
            except Exception as e:
                # 记录错误但不中断整个批量操作
                print(f"⚠️ 初始化 {data.get('stock_code')} 失败：{e}")

        return positions
