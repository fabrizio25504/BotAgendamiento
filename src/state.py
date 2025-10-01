from typing import TypedDict

class AgentState(TypedDict):
    intencion : str
    nombre : str | None
    fecha : str | None
    hora : str | None
    historial : list[str]
    cita_valida : bool
    error : bool