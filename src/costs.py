"""Supuestos de costes. Fracciones por lado (0.001 = 0,10%).

Comisiones no verificadas en vivo (Binance bloqueado por la red del entorno):
se usa el supuesto conservador de CLAUDE.md.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Costs:
    fee: float       # comisión por lado
    slippage: float  # slippage por lado

    @property
    def per_side(self) -> float:
        return self.fee + self.slippage

    def scaled(self, k: float) -> "Costs":
        return Costs(self.fee * k, self.slippage * k)


SPOT = Costs(fee=0.0010, slippage=0.0005)
PERP = Costs(fee=0.0005, slippage=0.0005)
MIN_NOTIONAL_USD = 5.0   # spot ~5 USD; perps BTC/ETH tienen mínimos mayores (verificar)
CAPITAL_USD = 1000.0
