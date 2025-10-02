from langgraph.graph import StateGraph, START, END
from state import AgentState
from funcionalidades import *
import json
from prompts import * 

def inicio(state : AgentState) -> AgentState:
    "Nodo inicial de donde debes detectar la primera intencion"
    print("- Hola! Soy tu asistente virtual para agendar citas, consultar disponibilidad o cancelar. ¿En qué puedo ayudarte hoy?")
    print("- Inicia agregando o tu nombre o la fecha que deseas agendar o cancelar o consultar.")
    input_text = input("Usuario: ")
    
    state["intencion"] = invoke_model( input_text, promptInicio)
    state["historial"] = [f"Usuario: {input_text}"]
    return state


# Anotacion el flujo tambien podría ir primero por pedir fecha y luego por pedir nombre
def pedirNombre(state : AgentState) -> AgentState:
    """ Nodo para pedir el nombre del usuario luego de haber detectado intencion 'nombre'"""
    
    #print("estoy pasando por pedir nombre")
    if state.get("fecha") is not None:
        print("- ¿Disculpa, Cuál es tu nombre?")
        input_text = input("Usuario: ")
        state["nombre"] = invoke_model( input_text, promptObtenerNombre)
        #state["intencion"] = "Finalizar"  # forzar a que la siguiente intencion sea finalizar
    elif state.get("fecha") is None:
        #print("paso por el else de pedir nombre")
        state["nombre"] = invoke_model( state["historial"][-1], promptObtenerNombre)
        #state["intencion"] = "PedirFecha"  # forzar a que la siguiente intencion sea pedir fecha

    return state

def pedirFecha(state : AgentState) -> AgentState:
    """ Nodo para pedir la fecha de la cita luego de haber detectado intencion 'fecha'""" 
    
    
    #print("estoy pasando por pedir fecha")
    #print(state)
    # Caso 1: Reintento después de error

    if state.get("hora") == "error" and state.get("fecha") != "error" and state.get("fecha") is not None:
        print("- La hora proporcionada no es válida o no proporcionaste. Vuelve a proporcionar la fecha y hora.")
        #agregar mensaje de fechas disponibles
        print("- Fechas disponibles: 30/09/2025 al 13/10/2025. Horas: 9-12 y 14-17 (en punto).")
        horarios_disponibles = ", ".join(obtener_horarios_disponibles(state['fecha'], disponibilidadTotal()))
        print(f"los horarios disponibles del {state['fecha']} son: {horarios_disponibles}")
        state["historial"].append(f"bot: los horarios disponibles del {state['fecha']} son: {horarios_disponibles}")
        input_text = input("Usuario: ")
        state["historial"].append(f" Usuario: {input_text}")
        print(state["historial"][-2]+state["historial"][-1])
        output = invoke_model(state["historial"][-2]+state["historial"][-1], promptObtenerFecha)
        #output = invoke_model(input_text, promptObtenerFecha)
        #print(output)
        state = parsearFechaHora(output, state)

    elif state.get("fecha") == "error" :
        print("- La fecha u hora proporcionada no es válida. Por favor, sé más específico.")
        print("- Fechas disponibles: 30/09/2025 al 14/10/2025. Horas: 9-12 y 14-17 .")
        input_text = input("Usuario: ")
        output = invoke_model(input_text, promptObtenerFecha)
        #print(output)
        state = parsearFechaHora(output, state)
    
    # Caso 2: Ya tenemos nombre, solo falta fecha
    elif state.get("nombre") is not None and state.get("fecha") is None:
        print("- ¿Qué fecha prefieres para tu cita?")
        input_text = input("Usuario: ")
        state["fecha"] = invoke_model(input_text, promptObtenerFecha)
        output = invoke_model(input_text, promptObtenerFecha)
        #print(output)
        state = parsearFechaHora(output, state)
    
    # Caso 3: Tenemos fecha en historial, no tenemos nombre
    elif state.get("nombre") is None and state.get("fecha") is None:
        output = invoke_model(state["historial"][-1], promptObtenerFecha)
        #print(output)
        state = parsearFechaHora(output, state)
    
    elif state.get("cita_valida") == False:
        print("- Por favor, proporciona una nueva fecha y hora para tu cita.")
        input_text = input("Usuario: ")
        output = invoke_model(input_text, promptObtenerFecha)
        #print(output)
        state = parsearFechaHora(output, state)
    
    else:
        print("Volviendo a pedir fecha.")
        print("- Por favor, proporciona una nueva fecha y hora para tu cita.")
        input_text = input("Usuario: ")
        state["historial"].append(f" Usuario: {input_text}")
        output = invoke_model(state["historial"][-2]+state["historial"][-1], promptObtenerFecha)
        #print(output)
        state = parsearFechaHora(output, state)
        
    return state

def confirmar(state : AgentState) -> AgentState:
    """ Nodo para confirmar una cita en base a disponibilidad"""
    #El confirmar no devuelve a pedir fecha si el usuario desea otra fecha
    #print("estoy pasando por confirmar")
    if confirmarHora(state["hora"], state["fecha"], disponibilidadTotal()):
        print(f"- Entonces confirmas tu cita en el horario {state['fecha']} - {state['hora']}, ¿correcto?")
        state["cita_valida"] = True
        
    else : 
        # TODO imprimir las fechas y horas disponibles de ese dia
        print(f"- Lo siento, el horario {state['fecha']} - {state['hora']} no está disponible. Por favor, elige otro horario.")
        print(f"- Horarios disponibles de ese día: ", {', '.join(obtener_horarios_disponibles(state['fecha'], disponibilidadTotal()))})
        respuesta_bot = f"- Horarios disponibles de ese día: {', '.join(obtener_horarios_disponibles(state['fecha'], disponibilidadTotal()))}"
        state["historial"].append(f"bot: {respuesta_bot}")
        state["cita_valida"] = False
        return state
    
    input_text = input("Usuario: ")
    state["historial"].append(f"Usuario: {input_text}")
      
    return state


def consultarDisponibilidad(state: AgentState) -> AgentState:
    """
    Nodo que define que tipo de disponibilidad se consulta (dia completo o hora especifica)
    luego de haber detectado intencion de preguntar una fecha u hora especifica
    """
    #print("estoy pasando por consultar disponibilidad")
    respuesta_str = invoke_model(state["historial"][-1], promptConsultarDisponibilidad).replace("```", '').replace("json", '').strip()
    #print("respuesta str : ", respuesta_str)
    try :
        respuesta = json.loads(respuesta_str)
    except json.JSONDecodeError:
        respuesta = {"fecha": None, "hora": None}
    #print(respuesta)
    fecha = respuesta.get("fecha")
    hora = respuesta.get("hora")
    
    # El nodo (Mesero) llama a la lógica (Chef)
    disponibilidad = disponibilidadTotal()

    if hora:
        # --- CASO 1: Consulta por hora específica ---
        print(f"Revisando disponibilidad para el {fecha} a las {hora}...")
        
        if confirmarHora(hora, fecha, disponibilidad):
            print("- ¡Sí, ese horario está disponible! ¿Deseas pasar a la confirmacion?")
            state["historial"].append(f"bot: ¡Sí, ese horario está disponible! ¿Deseas pasar a la confirmacion?")
            state["fecha"] = fecha
            state["hora"] = hora
        else:
            mensaje_bot_1 = f"- Lo siento, el horario de las {hora} ya está ocupado."
            print(mensaje_bot_1)
            
            horarios_libres = obtener_horarios_disponibles(fecha, disponibilidad)
            state["historial"].append(f"bot: {mensaje_bot_1}")
            if horarios_libres:
                mensaje_bot_2 = f"Para el {fecha} aún tengo libre: {', '.join(horarios_libres)}."
                mensaje_bot_3 = "¿Prefieres alguno de estos?"
                print(mensaje_bot_2)
                print(mensaje_bot_3)
                state["historial"].append(f"bot: {mensaje_bot_2}")
                state["historial"].append(f"bot: {mensaje_bot_3}")
            else:
                mensaje_bot_2 = "De hecho, ya no me quedan horarios para ese día."
                print(mensaje_bot_2)
                state["historial"].append(f"bot: {mensaje_bot_2}")
    else:
        # --- CASO 2: Consulta por día completo ---
        print(f"- Buscando horarios disponibles para el {fecha}...")
        horarios_libres = obtener_horarios_disponibles(fecha, disponibilidad)
        
        if horarios_libres:
            # El Mesero formatea los datos para el usuario con .join()
            mensaje_bot = f"- Para el {fecha} las horas disponibles son: {', '.join(horarios_libres)}"
            mensaje_bot_2 = "- ¿Te gustaría agendar en alguno de esos horarios? Por favor, indica la hora."
            print(mensaje_bot)
            print(mensaje_bot_2)
            state["historial"].append(f"bot: {mensaje_bot}")
            state["historial"].append(f"bot: {mensaje_bot_2}")
            state["fecha"] = fecha
        else:
            mensaje_bot= f"- Lo siento, no me quedan horarios disponibles para el {fecha}. \n¿Te gustaría consultar otro día? De ser así indica la fecha y hora"
            print(mensaje_bot)
            # AÑADIDO: Guardar ambos mensajes
            state["historial"].append(f"bot: {mensaje_bot}")

    input_text = input("Usuario: ")
    state["historial"].append(f"Usuario: {input_text}")
     
    return state

def prepararConfirmacion(state : AgentState) -> AgentState:
    """ Nodo para preparar el mensaje de confirmacion añadiendo hora al estado """
    #print("estoy pasando por preparar confirmacion")
    if state.get("hora"):
        state["error"] = False
        
    else :
        hora_elegida = invoke_model(state["historial"][-1], promptObtenerHora)
        if hora_elegida != "error" :
            state["hora"] = hora_elegida
            state["error"] = False
        else:
            state["error"] = True
            
    return state

def cancelar(state: AgentState) -> AgentState:
    """
    Nodo inteligente para cancelar una cita.
    - Si no tiene los datos, los extrae del historial del usuario.
    - Si ya tiene los datos, ejecuta la cancelación.
    """
    # Escenario 1: No tenemos los detalles, necesitamos extraerlos.
    if not state.get("fecha") or not state.get("hora"):
        #print("INFO: No se encontraron fecha/hora en el estado. Consultando al modelo...")
        contexto_chat = "\n".join(state["historial"])
        
        # Usamos el nuevo promptCancelar
        respuesta_modelo = invoke_model(contexto_chat, promptCancelar).replace("```", '').replace("json", '').strip()
        #print("Respuesta del modelo para cancelar:", respuesta_modelo)
        try:
            datos_cita = json.loads(respuesta_modelo)
            fecha_extraida = datos_cita.get("fecha")
            hora_extraida = datos_cita.get("hora")
            
            if fecha_extraida == "error" or hora_extraida == "error":
                mensaje_bot = "Error ingresa la fecha y hora en formato correcto (YYYY-MM-DD y HH:MM) la siguiente vez."
                print(mensaje_bot)
                state["historial"].append(f"bot: {mensaje_bot}")
                return state

            # Actualizamos el estado con los datos extraídos.
            #print(f"INFO: Modelo extrajo -> Fecha: {fecha_extraida}, Hora: {hora_extraida}")
            state["fecha"] = fecha_extraida
            state["hora"] = hora_extraida

        except (json.JSONDecodeError, AttributeError):
            mensaje_bot = "- No entendí bien los detalles. ¿Me puedes repetir la fecha y hora de la cita a cancelar?"
            print(respuesta_modelo)
            state["historial"].append(f"bot: {mensaje_bot}")
            return state

    # Escenario 2: Ya tenemos los detalles, procedemos a cancelar.
    if state.get("fecha") and state.get("hora"):
        print(f"INFO: Procediendo a cancelar la cita para {state['fecha']} a las {state['hora']}...")
        
        if actualizar_y_guardar_disponibilidad(state["fecha"], state["hora"], True, "disponibilidad.json"):
            mensaje_bot = f"- Listo. La cita para el {state['fecha']} a las {state['hora']} ha sido cancelada exitosamente."
            print(mensaje_bot)
        else:
            mensaje_bot = "- Lo siento, no pude encontrar una cita con esos detalles para cancelar."
        
        state["fecha"] = None
        state["hora"] = None
        state["historial"].append(f"bot: {mensaje_bot}")
        
    return state

def finalizar (state : AgentState) -> AgentState:
    """ Nodo para finalizar el flujo """
    print(f"- El flujo ha terminado")
    return state

