from typing import TypedDict

class AgentState(TypedDict):
    intencion : str
    nombre : str | None
    fecha : str | None
    hora : str | None
    historial : str
    cita_valida : bool