from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from state import AgentState
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError 
from IPython.display import Image, display
from funcionalidades import invoke_model
from nodes import *
from enrutadores import *


load_dotenv()



graph  = StateGraph(AgentState)

### añadir nodos al grafo

graph.add_node("inicio", inicio)
graph.add_node("PedirNombre", pedirNombre)
graph.add_node("PedirFecha", pedirFecha)
graph.add_node("Finalizar", finalizar)
graph.add_node("Confirmar", confirmar)
graph.add_node("ConsultarDisponibilidad", consultarDisponibilidad)
graph.add_node("PrepararConfirmacion", prepararConfirmacion)
graph.add_node("Cancelar", cancelar)

### añadir transiciones entre nodos

graph.add_edge(START, "inicio")
graph.add_conditional_edges(
    "inicio",
    decidirRuta,
    {
        "goTo_PedirNombre": "PedirNombre",
        "goTo_PedirFecha": "PedirFecha",
        "goTo_Finalizar": "Finalizar",
        "goTo_ConsultarDisponibilidad": "ConsultarDisponibilidad",
        "goTo_Cancelar": "Cancelar"
    }
)
graph.add_conditional_edges(
    "PedirNombre",
    siguienteNodo,
    {
        "goTo_PedirFecha": "PedirFecha",
        "goTo_Confirmar": "Confirmar"
    }
)

graph.add_conditional_edges(
    "PedirFecha",
    siguienteNodo,
    {
        "goTo_PedirNombre": "PedirNombre",
        "goTo_Confirmar": "Confirmar",
        "goTo_PedirFecha": "PedirFecha"
    }
)

graph.add_conditional_edges(
    "Confirmar",
    enrutadorConfirmacion,
    {
        "goTo_Finalizar": "Finalizar",
        "goTo_Cancelar": "Cancelar",
        "goTo_PedirFecha": "PedirFecha"
    }
)

graph.add_conditional_edges(
    "ConsultarDisponibilidad",
    enrutadorConsultarDisponibilidad,
    {
        "goTo_Confirmar": "PrepararConfirmacion",
        "goTo_PedirFecha": "PedirFecha",
        "goTo_Finalizar": "Finalizar"
    }
)

graph.add_conditional_edges(
    "PrepararConfirmacion",
    lambda state: "goTo_Finalizar" if state.get("error") else "goTo_Confirmar",
    {
        "goTo_Finalizar": "Finalizar",
        "goTo_Confirmar": "Confirmar",
    }
                            )
graph.add_edge("Cancelar",END)
graph.add_edge("Finalizar",END)

app = graph.compile()
#graph_image = app.get_graph().draw_mermaid_png()
#with open("diagrams/mi_grafo.png", "wb") as f:
#    f.write(graph_image)
print(app.invoke({}))