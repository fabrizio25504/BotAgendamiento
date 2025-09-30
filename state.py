from typing import TypedDict

class AgentState(TypedDict):
    intencion : str
    nombre : str | None
    fecha : str | None
    historial : str