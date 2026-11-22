"""価格調整・課税・関税のアニメーション（第 8・9・10 章）。"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.patches import Polygon

from lib.animations.common import linear_values, make_animation
from lib.chapter08.market import (
    LinearMarket,
    equilibrium,
    excess_demand,
    quantity_demanded,
    quantity_supplied,
    walras_adjustment,
)
from lib.chapter09.surplus import TaxResult, tax_equilibrium
from lib.chapter10.trade import TradeResult, free_trade_result, tariff_result

_MARKET = LinearMarket(100, -1, -10, 1)
_PRICES = [float(p) for p in range(0, 101)]
_ALPHA = 0.3


def _draw_curves(ax: Axes, market: LinearMarket) -> None:
    ax.plot([quantity_demanded(market, p) for p in _PRICES], _PRICES, label="Demand")
    ax.plot([quantity_supplied(market, p) for p in _PRICES], _PRICES, label="Supply")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Quantity Q")
    ax.set_ylabel("Price P")


def _patch(label: str, color: str) -> Polygon:
    return Polygon([(0, 0)], closed=True, alpha=_ALPHA, label=label, facecolor=color)


def animate_price_adjustment(
    market: LinearMarket = _MARKET,
    price0: float = 80.0,
    speed: float = 0.25,
    steps: int = 20,
) -> FuncAnimation:
    """ワルラス的調整。価格が、超過需要に応じて動き、均衡へ近づく。"""
    path = walras_adjustment(market, price0, speed, steps)
    fig, ax = plt.subplots()
    _draw_curves(ax, market)
    (level,) = ax.plot([], [], linestyle="--", label="Price")
    (gap,) = ax.plot([], [], label="Excess demand")
    (demand_point,) = ax.plot([], [], "o", label="Demanded")
    (supply_point,) = ax.plot([], [], "o", label="Supplied")
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        price = path[i]
        qd, qs = quantity_demanded(market, price), quantity_supplied(market, price)
        level.set_data([0, 100], [price, price])
        gap.set_data([qs, qd], [price, price])
        demand_point.set_data([qd], [price])
        supply_point.set_data([qs], [price])
        excess = excess_demand(market, price)
        state = "excess supply" if excess < 0 else "excess demand"
        label.set_text(f"Step {i}: P = {price:.1f} ({state})")

    plt.close(fig)
    return make_animation(fig, update, len(path))


def tax_frames(market: LinearMarket, max_tax: float, frames: int) -> list[TaxResult]:
    """税額を 0 から max_tax へ動かしたときの、各フレームの結果。"""
    return [tax_equilibrium(market, t) for t in linear_values(0.0, max_tax, frames)]


def animate_tax(
    market: LinearMarket = _MARKET, max_tax: float = 20.0, frames: int = 30
) -> FuncAnimation:
    """税額が増えると、供給曲線が上へ動き、税収の長方形と死荷重の三角形が現れる。"""
    taxes = linear_values(0.0, max_tax, frames)
    data = tax_frames(market, max_tax, frames)
    eq_price, eq_quantity = equilibrium(market)
    fig, ax = plt.subplots()
    _draw_curves(ax, market)
    (shifted,) = ax.plot([], [], linestyle="--", label="Supply with tax")
    revenue = _patch("Tax revenue", "tab:purple")
    loss = _patch("Deadweight loss", "tab:red")
    ax.add_patch(revenue)
    ax.add_patch(loss)
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        tax, frame = taxes[i], data[i]
        shifted.set_data(
            [quantity_supplied(market, max(0.0, p - tax)) for p in _PRICES], _PRICES
        )
        q, pd, ps = frame.quantity, frame.buyer_price, frame.seller_price
        revenue.set_xy([(0, ps), (q, ps), (q, pd), (0, pd)])
        loss.set_xy([(q, pd), (q, ps), (eq_quantity, eq_price)])
        label.set_text(
            f"Tax = {tax:.1f}, revenue = {frame.tax_revenue:.1f}, "
            f"loss = {frame.deadweight_loss:.1f}"
        )

    plt.close(fig)
    return make_animation(fig, update, frames)


def tariff_frames(
    market: LinearMarket, world_price: float, max_tariff: float, frames: int
) -> list[TradeResult]:
    """関税を 0 から max_tariff へ動かしたときの、各フレームの結果。"""
    return [
        tariff_result(market, world_price, t)
        for t in linear_values(0.0, max_tariff, frames)
    ]


def animate_tariff(
    market: LinearMarket = _MARKET,
    world_price: float = 40.0,
    max_tariff: float = 15.0,
    frames: int = 30,
) -> FuncAnimation:
    """関税が増えると、国内価格が上がり、関税収入と、2 つの死荷重の三角形が現れる。"""
    data = tariff_frames(market, world_price, max_tariff, frames)
    free = free_trade_result(market, world_price)
    fig, ax = plt.subplots()
    _draw_curves(ax, market)
    ax.plot([0, 100], [world_price, world_price], linestyle=":", label="World price")
    (domestic,) = ax.plot([], [], linestyle="--", label="Domestic price")
    revenue = _patch("Tariff revenue", "tab:purple")
    production = _patch("Production loss", "tab:brown")
    consumption = _patch("Consumption loss", "tab:pink")
    for patch in (revenue, production, consumption):
        ax.add_patch(patch)
    label = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")
    ax.legend(fontsize="x-small", loc="upper right")

    def update(i: int) -> None:
        frame = data[i]
        pd = frame.domestic_price
        qs, qd = frame.quantity_supplied, frame.quantity_demanded
        domestic.set_data([0, 100], [pd, pd])
        revenue.set_xy([(qs, world_price), (qd, world_price), (qd, pd), (qs, pd)])
        production.set_xy(
            [(free.quantity_supplied, world_price), (qs, world_price), (qs, pd)]
        )
        consumption.set_xy(
            [(qd, pd), (free.quantity_demanded, world_price), (qd, world_price)]
        )
        loss = free.total_surplus - frame.total_surplus
        label.set_text(f"Domestic P = {pd:.1f}, loss = {loss:.1f}")

    plt.close(fig)
    return make_animation(fig, update, frames)
