from langgraph.graph import StateGraph, START, END
from state import AgentState
from funcionalidades import invoke_model, disponibilidadTotal, obtener_horarios_disponibles, confirmarHora, parsearFechaHora, actualizar_y_guardar_disponibilidad
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
    
def decidirRuta(state : AgentState) -> str:
    print(state["intencion"])
    if state["intencion"] == "PedirNombre":
        return "goTo_PedirNombre"
    elif state["intencion"] == "PedirFecha":
        return "goTo_PedirFecha"
    elif state["intencion"] == "Finalizar":
        return "goTo_Finalizar"
    elif state["intencion"] == "ConsultarDisponibilidad":
        return "goTo_ConsultarDisponibilidad"
    elif state["intencion"] == "Cancelar":
        return "goTo_Cancelar"
    
def siguienteNodo(state: AgentState) -> str:
    """Funcion para decidir el siguiente nodo basado en que estados faltan"""
    if state.get("fecha") == "error"or state.get("hora") == "error":
        # No resetear la fecha aquí, dejar que pedirFecha maneje el reintento
        return "goTo_PedirFecha"
    elif state.get("nombre") is None:
        return "goTo_PedirNombre"
    elif state.get("fecha") is None:
        return "goTo_PedirFecha"
    else:
        return "goTo_Confirmar"

def enrutadorConfirmacion(state : AgentState) -> str:
    """Funcion para decidir el siguiente nodo basado en la confirmacion del usuario"""
    if state.get("cita_valida") == True:
        prompt = f"""
        Usuario: {state['historial'][-1]}
        
        """
        #print(state["historial"][-1])
        state["intencion"] = invoke_model(prompt, promptObtenerConfirmacion)
        print("intencion confirmacion enrutador : ",state["intencion"])
        if state["intencion"] == "cancelar":
            print("El usuario ha decidido cancelar la cita.")
            return "goTo_Cancelar"
        elif state["intencion"] == "confirmar":
            print("debuggin confirmar")
            actualizar_y_guardar_disponibilidad(state["fecha"], state["hora"], False, "disponibilidad.json")   
            return "goTo_Finalizar"
        elif state["intencion"] == "pedirFecha":
            return "goTo_PedirFecha"
        else :
            print(f"No se entendió la intención {state['intencion']}, pidiendo fecha de nuevo.")
            return "goTo_Finalizar"
        
    else :
        return "goTo_PedirFecha"
