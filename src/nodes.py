from langgraph.graph import StateGraph, START, END
from state import AgentState
from funcionalidades import invoke_model, disponibilidadTotal, obtener_horarios_disponibles, confirmarHora, parsearFechaHora
import json
from prompts import * 

def inicio(state : AgentState) -> AgentState:
    "Nodo inicial de donde debes detectar la primera intencion"
    print("Hola! Soy tu asistente virtual para agendar citas. ¿En qué puedo ayudarte hoy?")
    input_text = input("Usuario: ")
    
    state["intencion"] = invoke_model( input_text, promptInicio)
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
    elif state["intencion"] == "ConsultarDisponibilidad":
        return "goTo_ConsultarDisponibilidad"
    
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

# Anotacion el flujo tambien podría ir primero por pedir fecha y luego por pedir nombre
def pedirNombre(state : AgentState) -> AgentState:
    """ Nodo para pedir el nombre del usuario luego de haber detectado intencion 'nombre'"""
    
    print("estoy pasando por pedir nombre")
    if state.get("fecha") is not None:
        print("¿Cuál es tu nombre?")
        input_text = input("Usuario: ")
        state["nombre"] = invoke_model( input_text, promptObtenerNombre)
        #state["intencion"] = "Finalizar"  # forzar a que la siguiente intencion sea finalizar
    elif state.get("fecha") is None:
        print("paso por el else de pedir nombre")
        state["nombre"] = invoke_model( state["historial"], promptObtenerNombre)
        #state["intencion"] = "PedirFecha"  # forzar a que la siguiente intencion sea pedir fecha

    return state

def pedirFecha(state : AgentState) -> AgentState:
    """ Nodo para pedir la fecha de la cita luego de haber detectado intencion 'fecha'""" 
    
    
    print("estoy pasando por pedir fecha")
    print(state)
    # Caso 1: Reintento después de error
    if state.get("fecha") == "error":
        print("La fecha u hora proporcionada no es válida. Por favor, sé más específico.")
        print("Fechas disponibles: 30/09/2025 al 14/10/2025. Horas: 9-12 y 14-17 (en punto).")
        input_text = input("Usuario: ")
        output = invoke_model(input_text, promptObtenerFecha)
        print(output)
        state = parsearFechaHora(output, state)
    
    # Caso 2: Ya tenemos nombre, solo falta fecha
    elif state.get("nombre") is not None and state.get("fecha") is None:
        print("¿Qué fecha prefieres para tu cita?")
        input_text = input("Usuario: ")
        state["fecha"] = invoke_model(input_text, promptObtenerFecha)
        output = invoke_model(input_text, promptObtenerFecha)
        print(output)
        state = parsearFechaHora(output, state)
    
    # Caso 3: Tenemos fecha en historial, no tenemos nombre
    elif state.get("nombre") is None and state.get("fecha") is None:
        output = invoke_model(state["historial"], promptObtenerFecha)
        print(output)
        state = parsearFechaHora(output, state)
    
    elif state.get("cita_valida") == False:
        print("Por favor, proporciona una nueva fecha y hora para tu cita.")
        input_text = input("Usuario: ")
        output = invoke_model(input_text, promptObtenerFecha)
        print(output)
        state = parsearFechaHora(output, state)
        
    return state

def confirmar(state : AgentState) -> AgentState:
    """ Nodo para confirmar una cita en base a disponibilidad"""
    print("estoy pasando por confirmar")
    if confirmarHora(state["hora"], state["fecha"], disponibilidadTotal()):
        print(f"Entonces confirmas tu cita en el horario {state['fecha']} - {state['hora']}, ¿correcto?")
        state["cita_valida"] = True
        
    else : 
        # TODO imprimir las fechas y horas disponibles de ese dia
        print(f"Lo siento, el horario {state['fecha']} - {state['hora']} no está disponible. Por favor, elige otro horario.")
        print(f"fechas disponibles : ", {', '.join(obtener_horarios_disponibles(state['fecha'], disponibilidadTotal()))})
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
        print(state["historial"])
        state["intencion"] = invoke_model(prompt, promptObtenerConfirmacion)
        print("intencion confirmacion enrutador : ",state["intencion"])
        if state["intencion"] == "cancelar":
            print("El usuario ha decidido cancelar la cita.")
            return "goTo_Finalizar" # cambiar a finalizar por ahora luego a cancelar 
        elif state["intencion"] == "confirmar":
            return "goTo_Finalizar"
        
    else :
        return "goTo_PedirFecha"

def consultarDisponibilidad(state: AgentState) -> AgentState:
    """
    Nodo que define que tipo de disponibilidad se consulta (dia completo o hora especifica)
    luego de haber detectado intencion de preguntar una fecha u hora especifica
    """
    #print("estoy pasando por consultar disponibilidad")
    respuesta_str = invoke_model(state["historial"], promptConsultarDisponibilidad).replace("```", '').replace("json", '').strip()
    print("respuesta str : ", respuesta_str)
    try :
        respuesta = json.loads(respuesta_str)
    except json.JSONDecodeError:
        respuesta = {"fecha": None, "hora": None}
    print(respuesta)
    fecha = respuesta.get("fecha")
    hora = respuesta.get("hora")
    
    # El nodo (Mesero) llama a la lógica (Chef)
    disponibilidad = disponibilidadTotal()

    if hora:
        # --- CASO 1: Consulta por hora específica ---
        print(f"Revisando disponibilidad para el {fecha} a las {hora}...")
        
        if confirmarHora(hora, fecha, disponibilidad):
            print("¡Sí, ese horario está disponible! ¿Deseas pasar a la confirmacion?")
            state["historial"] = f"bot: ¡Sí, ese horario está disponible! ¿Deseas pasar a la confirmacion?)"
            state["fecha"] = fecha
            state["hora"] = hora
        else:
            print(f"Lo siento, el horario de las {hora} ya está ocupado.")
            # El Mesero pide más datos al Chef para ser más útil
            horarios_libres = obtener_horarios_disponibles(fecha, disponibilidad)
            if horarios_libres:
                print(f"Para el {fecha} aún tengo libre: {', '.join(horarios_libres)}.")
                print("¿Prefieres alguno de estos?")
            else:
                print("De hecho, ya no me quedan horarios para ese día.")
    else:
        # --- CASO 2: Consulta por día completo ---
        print(f"Buscando horarios disponibles para el {fecha}...")
        horarios_libres = obtener_horarios_disponibles(fecha, disponibilidad)
        
        if horarios_libres:
            # El Mesero formatea los datos para el usuario con .join()
            print(f"Para el {fecha} las horas disponibles son: {', '.join(horarios_libres)}")
            print("¿Te gustaría agendar en alguno de esos horarios? Por favor, indica la hora.")
            state["fecha"] = fecha
        else:
            print(f"Lo siento, no me quedan horarios disponibles para el {fecha}.")
            print("¿Te gustaría consultar otro día?")

    input_text = input("Usuario: ")
    state["historial"] += input_text
     
    return state

def prepararConfirmacion(state : AgentState) -> AgentState:
    """ Nodo para preparar el mensaje de confirmacion añadiendo hora al estado """
    print("estoy pasando por preparar confirmacion")
    if state.get("hora"):
        state["error"] = False
        
    else :
        hora_elegida = invoke_model(state["historial"], promptObtenerHora)
        if hora_elegida != "error" :
            state["hora"] = hora_elegida
            state["error"] = False
        else:
            state["error"] = True
            
    return state

def finalizar (state : AgentState) -> AgentState:
    """ Nodo para finalizar el flujo """
    print(f"El flujo ha terminado")
    return state

