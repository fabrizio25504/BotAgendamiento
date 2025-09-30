from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from state import AgentState
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError 
from IPython.display import Image, display

load_dotenv()

api_key_name = "BedrockAPIKey-jw6j-at-994142413059"
api_key = "ABSKQmVkcm9ja0FQSUtleS1qdzZqLWF0LTk5NDE0MjQxMzA1OTpEQTNRQUxVSnNweFgwRnlDOXpBcHdIMkU0WlBQOElnWU1aMVlxNFliUVdCZnlVb3VrbjVXMlhJdVR2dz0="
#export AWS_BEARER_TOKEN_BEDROCK=ABSKQmVkcm9ja0FQSUtleS1qdzZqLWF0LTk5NDE0MjQxMzA1OTpEQTNRQUxVSnNweFgwRnlDOXpBcHdIMkU0WlBQOElnWU1aMVlxNFliUVdCZnlVb3VrbjVXMlhJdVR2dz0=

def obtenerModelo():
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    return client

def invoke_model(state : AgentState, prompt: str, system: str) -> AgentState:
    client = obtenerModelo()
    try:
        response = client.converse(
            modelId="us.amazon.nova-pro-v1:0",
            messages = [{
                "role": "user",
                "content": [{"text":prompt}]
            }],
            system = [{"text" : system}],
            inferenceConfig = {
                "maxTokens": 100,
                "temperature": 0.0,
            }
        )
        return response["output"]["message"]["content"][0]["text"]
    except ClientError as e:
        print(f"Error invoking model: {e}")
        return "Error"

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
    state["intencion"] = invoke_model(state, input_text, systemPrompt)
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
    

# Anotacion el flujo tambien podría ir primero por pedir fecha y luego por pedir nombre
def pedirNombre(state : AgentState) -> AgentState:
    """ Nodo para pedir el nombre del usuario luego de haber detectado intencion 'nombre'"""
    systemPrompt = """
        Eres un asistente que detecta el nombre del usuario. Responde con solo el nombre del usuario.
        Es posible que el usuario te de más texto a parte del nombre.
        Solo responde con el nombre, no des explicaciones.
        """
    print("estoy pasando por pedir nombre")
    if state.get("fecha") is not None:
        print("¿Cuál es tu nombre?")
        input_text = input("Usuario: ")
        state["nombre"] = invoke_model(state, input_text, systemPrompt)
        state["intencion"] = "Finalizar"  # forzar a que la siguiente intencion sea finalizar
    elif state.get("fecha") is None:
        print("paso por el else de pedir nombre")
        state["nombre"] = invoke_model(state, state["historial"], systemPrompt)
        state["intencion"] = "PedirFecha"  # forzar a que la siguiente intencion sea pedir fecha

    return state

def pedirFecha(state : AgentState) -> AgentState:
    """ Nodo para pedir la fecha de la cita luego de haber detectado intencion 'fecha'""" 
    systemPrompt = """
    Eres un asistente que detecta la fecha que el usuario quiere para agendar una cita.
    Responde con solo la fecha en formato DD/MM/AAAA.
    Es posible que el usuario te de más texto a parte de la fecha.
    Recuerda que el año actual es 2025
    """
    print("estoy pasando por pedir fecha")
    if state.get("nombre") is not None:
        print("¿Qué fecha prefieres para tu cita?")
        input_text = input("Usuario: ")
        state["fecha"] = invoke_model(state, input_text, systemPrompt)
        state["intencion"] = "Finalizar"  # forzar a que la siguiente intencion sea finalizar
    elif state.get("nombre") is None:
        state["fecha"] = invoke_model(state, state["historial"], systemPrompt)
        state["intencion"] = "PedirNombre"  # forzar a que la siguiente intencion sea pedir nombre

def Finalizar (state : AgentState) -> AgentState:
    """ Nodo para finalizar el flujo """
    print(f"El flujo ha terminado")
    return state


graph  = StateGraph(AgentState)

### añadir nodos al grafo

graph.add_node("inicio", inicio)
graph.add_node("PedirNombre", pedirNombre)
graph.add_node("PedirFecha", pedirFecha)
graph.add_node("finalizar", Finalizar)

### añadir transiciones entre nodos

graph.add_edge(START, "inicio")
graph.add_conditional_edges(
    "inicio",
    decidirRuta,
    {
        "goTo_PedirNombre": "PedirNombre",
        "goTo_PedirFecha": "PedirFecha",
        "goTo_Finalizar": "finalizar"
    }
)
graph.add_conditional_edges(
    "PedirNombre",
    decidirRuta,
    {
        "goTo_PedirFecha": "PedirFecha",
        "goTo_Finalizar": "finalizar"
    }
)

graph.add_conditional_edges(
    "PedirFecha",
    decidirRuta,
    {
        "goTo_PedirNombre": "PedirNombre",
        "goTo_Finalizar": "finalizar"
    }
)


graph.add_edge("finalizar",END)

app = graph.compile()

print(app.invoke({}))