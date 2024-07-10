"""
AIState is an enum class that represents the state of the AI.
"""

from enum import Enum


class AIState(Enum):
    """
    AIState is an enum class that represents the state of the AI.
    It has two states: SIMULATION and EVOLVING.
    When the AI is in the SIMULATION state, the AI agents are being simulated, and therefor the AI is not evolving,
    just running the simulation.
    When the AI is in the EVOLVING state, the AI agents are evolving.
    """
    SIMULATION = 1
    EVOLVING = 2
