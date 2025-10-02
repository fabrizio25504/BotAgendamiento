# 🤖 BotAgendamiento: Un Asistente Inteligente con LangGraph

Un bot conversacional construido con Python y LangGraph, capaz de gestionar el agendamiento, consulta y confirmación de citas de manera inteligente y natural. Este proyecto fue desarrollado como parte de una prueba técnica para demostrar habilidades en el manejo de grafos de estado y la integración con modelos de lenguaje.

## ✨ Características Principales

- Flujo Conversacional Basado en Grafos: Utiliza LangGraph para modelar la conversación como un grafo de estados, permitiendo flujos complejos, bucles y decisiones lógicas.

- Comprensión de Lenguaje Natural (NLU): Se integra con un LLM (a través de AWS Bedrock) para detectar intenciones (agendar, consultar, cancelar) y extraer entidades (fechas, horas, nombres).

- Gestión de Estado: Mantiene el contexto de la conversación a lo largo de diferentes turnos gracias a una clase estado ubicada en (src/state.py).

- Consulta de Disponibilidad: Interactúa con una fuente de datos simulada (disponibilidad.json) para verificar y ofrecer horarios (Usar solo fechas del 30 de setiembre al 13 de setiembre).


## 🛠️ Tecnologías Utilizadas

    Lenguaje: Python 3.12.10

    Framework de Grafo: LangGraph

    Modelo de Lenguaje: A través de AWS Bedrock (Boto3) con Amazon nova lite

    Gestión de Dependencias: Pip, requirements.txt

    Entorno: Variables de entorno (.env) (Puse credenciales temporales para que puedan usarlo sin problema tiene vigencia de una semana)

## 📊 Diagrama del Grafo

El flujo lógico de la conversación se modela con el siguiente grafo de estados:

<img width="784" height="496" alt="mi_grafo" src="https://github.com/user-attachments/assets/86c4a3e3-df62-405d-98b8-945260e9060a" />

Esta generado con **mermaid**

Y tambien esta el diagrama hecho con **draw.io**

en el archivo [/diagrams/pruebaTecnicaMaquinaDeEstados.jpg]

## 🚀 Instalación y Ejecución

Sigue estos pasos para poner en marcha el bot en tu máquina local.

1. Clona el repositorio:
**Bash**
```
git clone https://github.com/fabrizio25504/BotAgendamiento.git
cd BotAgendamiento
```
2. Crea y activa un entorno virtual (recomendado):
**Bash**
```
# En Windows
python -m venv venv

.\venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
3. Instala las dependencias:
Bash
```
pip install -r requirements.txt
```
4. Configura las variables de entorno:
Ya esta configurado en el .env


Ejecuta el bot:
**Bash**

    python src/main.py

## 💬 Uso y Flujos de Conversación

Una vez ejecutado, el bot te saludará. A continuación, se muestran algunos ejemplos de interacción.


[Flujos conversacionales.pdf](https://github.com/user-attachments/files/22665471/Flujos.conversacionales.pdf)

## Futuras mejoras
- Verificar más casos : Hay algunos casos que no contemple y simplemente el flujo se siento algo forzado o se termina como por ejemplo si quiero cancelar una fecha sin especificar la hora
- Mejorar prompts : Algunos prompts faltan ser refinados con ejemplos esto por ejemplo si insertas una hora sin decir si es pm o am puede confundir al modelo y darte un error
- Hacer algo con el nombre : Por falta de tiempo no pude implementar que las citas se agenden con el nombre que se pide durante el flujo pero si se marcan como ocupadas o desocupadas
- Ampliar las fechas : actualmente solo se aceptan fechas entre el 30 de setiembre y el 13 de octubre pues todo esta basado en un JSON con esas fechas

## 📁 Estructura del Proyecto
```
BotAgendamiento/
├── .gitignore
├── README.md
├── requirements.txt
├── disponibilidad.json
├── diagrams
    ├── mi_grafo.png     # Grafo generado en mermaid en el mismo codigo del main
    ├── grafo.io         # Grafo hecho en draw.io
└── src/
    ├── __init__.py
    ├── main.py         # Ensambla y ejecuta el grafo.
    ├── prompts.py      # Contiene los prompts que usa el modelo a lo largo del flujo
    ├── state.py        # Define la estructura del AgentState.
    ├── nodes.py        # Contiene las funciones de los nodos.
    ├── enrutadores.py      # Contiene las funciones de enrutamiento.
    └── funcionalidades.py # Funciones auxiliares (invoke_model, etc.).
```
