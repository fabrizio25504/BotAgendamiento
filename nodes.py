from langgraph.graph import StateGraph, START, END
from state import AgentState
from funcionalidades import invoke_model, disponibilidadTotal, confirmarDisponibilidad, confirmarHora

def inicio(state : AgentState) -> AgentState:
    "Nodo inicial de donde debes detectar la primera intencion"
    print("Hola! Soy tu asistente virtual para agendar citas. ¿En qué puedo ayudarte hoy?")
    input_text = input("Usuario: ")
    systemPrompt = """
    Eres un asistente que detecta la intencion del usuario. Responde con una sola palabra que sea la intencion principal del usuario.
    Las intenciones posibles son: 'PedirNombre' si el usuario quiere dar su nombre, 'PedirFecha' si el usuario quiere dar una fecha para agendar una cita, 
    'Finalizar' si el usuario quiere terminar la conversación. Si no entiendes la intencion responde 'Finalizar'.
    Solo responde con la intencion, no des explicaciones.
    """
    state["intencion"] = invoke_model( input_text, systemPrompt)
    state["historial"] = input_text
    return state

def decidirRuta(state : AgentState) -> str:
    print(state["intencion"])
    if state["intencion"] == "PedirNombre":
        return "goTo_PedirNombre"
    elif state["intencion"] == "PedirFecha":
        return "goTo_PedirFecha"
    elif state["intencion"] == "Finalizar":
        return "goTo_Finalizar"
    
def siguienteNodo(state: AgentState) -> str:
    """Funcion para decidir el siguiente nodo basado en que estados faltan"""
    if state.get("fecha") == "error":
        # No resetear la fecha aquí, dejar que pedirFecha maneje el reintento
        return "goTo_PedirFecha"
    elif state.get("nombre") is None:
        return "goTo_PedirNombre"
    elif state.get("fecha") is None:
        return "goTo_PedirFecha"
    else:
        return "goTo_Finalizar"

# Anotacion el flujo tambien podría ir primero por pedir fecha y luego por pedir nombre
def pedirNombre(state : AgentState) -> AgentState:
    """ Nodo para pedir el nombre del usuario luego de haber detectado intencion 'nombre'"""
    systemPrompt = """
        Eres un asistente que detecta el nombre completo del usuario. Responde con solo el nombre completo del usuario.
        Es posible que el usuario te de más texto a parte del nombre.
        Solo responde con el nombre completo, no des explicaciones.
        """
    print("estoy pasando por pedir nombre")
    if state.get("fecha") is not None:
        print("¿Cuál es tu nombre?")
        input_text = input("Usuario: ")
        state["nombre"] = invoke_model( input_text, systemPrompt)
        #state["intencion"] = "Finalizar"  # forzar a que la siguiente intencion sea finalizar
    elif state.get("fecha") is None:
        print("paso por el else de pedir nombre")
        state["nombre"] = invoke_model( state["historial"], systemPrompt)
        #state["intencion"] = "PedirFecha"  # forzar a que la siguiente intencion sea pedir fecha

    return state

def pedirFecha(state : AgentState) -> AgentState:
    """ Nodo para pedir la fecha de la cita luego de haber detectado intencion 'fecha'""" 
    systemPrompt = """
    <contexto>
    El usuario está tratando de agendar una cita. Ahora necesita proporcionar una fecha para la cita. 
    El mes actual es octubre de 2025.
    </contexto>
    <instrucciones>
    Extrae la fecha en formato AAAA-MM-DD del texto del usuario.
    Si la instruccion no contiene una fecha valida, responde "error".
    </instrucciones>
    <restricciones>
    Solo acepta fechas dentro de '2025-09-30' y '2025-10-14', que son las fechas disponibles.
    Y con las horas de 09:00 a 12:00 y de 14:00 a 17:00. Deben ser horas en punto.
    No debes aceptar si la fecha es ambigua. Ejemplo: "el próximo lunes" o "el 5" son ambiguos.
    </restricciones>
    <response format>
    Responde solo con la fecha en formato AAAA-MM-DD No des explicaciones.
    </response format>
    <examples>
    Usuario: Quisiera una cita el 5 de octubre de 2025.
    Asistente: '2025-10-05'
    </examples>
    """
    
    print("estoy pasando por pedir fecha")
    
    # Caso 1: Reintento después de error
    if state.get("fecha") == "error":
        print("La fecha proporcionada no es válida. Por favor, proporciona una fecha sin ambigüedades.")
        print("Las fechas disponibles son del 30/09/2025 al 14/10/2025.")
        input_text = input("Usuario: ")
        state["fecha"] = invoke_model(input_text, systemPrompt)
        state["historial"] = input_text
    
    # Caso 2: Ya tenemos nombre, solo falta fecha
    elif state.get("nombre") is not None and state.get("fecha") is None:
        print("¿Qué fecha prefieres para tu cita?")
        input_text = input("Usuario: ")
        state["fecha"] = invoke_model(input_text, systemPrompt)
        state["historial"] = input_text
    
    # Caso 3: Tenemos fecha en historial, no tenemos nombre
    elif state.get("nombre") is None and state.get("fecha") is None:
        state["fecha"] = invoke_model(state["historial"], systemPrompt)
        
    return state

def confirmar(state : AgentState) -> AgentState:
    """ Nodo para confirmar una cita en base a disponibilidad"""
    print("estoy pasando por confirmar")
    if confirmarHora(state["hora"], state["fecha"], disponibilidadTotal()):
        print(f"Entonces confirmas tu cita en el horario {state['fecha']} - {state['hora']}, ¿correcto?")
        state["cita_valida"] = True
        
    else : 
        print(f"Lo siento, el horario {state['fecha']} - {state['hora']} no está disponible. Por favor, elige otro horario.")
        state["cita_valida"] = False
        return state
    
    input_text = input("Usuario: ")
    state["historial"] =  input_text
      
    return state

def enrutadorConfirmacion(state : AgentState) -> str:
    """Funcion para decidir el siguiente nodo basado en la confirmacion del usuario"""
    if state.get("cita_valida") == True:
        prompt = f"""
        Usuario: {state['historial']}
        """
        systemPrompt = """Si detectas que el usuario desea cancelar su cita responde "cancelar", y si de lo contrario detectas una confirmacion responde "confirmar".
        """
        state["intencion"] = invoke_model(prompt, systemPrompt)
        
        if state["intencion"] == "cancelar":
            print("El usuario ha decidido cancelar la cita.")
            return "goTo_Finalizar" # cambiar a finalizar por ahora luego a cancelar 
        elif state["intencion"] == "confirmar":
            return "goTo_Finalizar"
        
    else :
        return "goTo_PedirFecha"

def finalizar (state : AgentState) -> AgentState:
    """ Nodo para finalizar el flujo """
    print(f"El flujo ha terminado")
    return state
