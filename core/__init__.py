# 林火蔓延多层元胞自动机核心模块
# Fire Spread Multi-Layer Cellular Automaton Core Module

__version__ = "1.0.0"
__author__ = "Fire Modeling Team"

# 导入核心类和函数
from .cell import Cell, CellState
from .fire_engine import FireEngine
from .cellular_automaton import CellularAutomaton

__all__ = [
    'Cell',
    'CellState', 
    'FireEngine',
    'CellularAutomaton'
] 