from langgraph.graph import StateGraph, START, END
from state import AgentState
from funcionalidades import invoke_model, disponibilidadTotal, obtener_horarios_disponibles, confirmarHora, parsearFechaHora
import json
from prompts import * 

def enrutadorConsultarDisponibilidad (state : AgentState) -> str :
    """ Nodo para consultar la disponibilidad de citas luego de haber detectado intencion
    de preguntar una fecha u hora especifica'"""
    goTo = invoke_model( "\n".join(state["historial"]), promptEnrutadorConsultarDisponibilidad)
    
    if goTo == "PedirFecha":
        return "goTo_PedirFecha"
    elif goTo == "Confirmar":
        return "goTo_Confirmar"
    elif goTo == "Finalizar":
        return "goTo_Finalizar"
    else :
        print(f"No se entendió la intención {goTo}, finalizando la conversación.")
        return "goTo_Finalizar"  