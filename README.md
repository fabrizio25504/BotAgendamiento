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

el el archivo [pruebaTecnicaMaquinaDeEstados.io]

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
python -m venv venv
# En Windows
.\venv\Scripts\activate
# En macOS/Linux
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

Flujo 1: Agendamiento Directo

    Usuario: Hola, quiero una cita para el 6 de octubre a las 3 de la tarde.

    Bot: (Detecta fecha y hora, verifica disponibilidad) ¡Sí, ese horario está disponible! ¿Deseas pasar a la confirmacion?

    Usuario: Sí, por favor.

    Bot: (Pasa por el nodo confirmar) Perfecto. ¿Confirmo tu cita para el 2025-10-06 a las 15:00?

    Usuario: Correcto.

    Bot: ¡Genial! Tu cita ha sido agendada.

Flujo 2: Consulta de Disponibilidad

    Usuario: ¿Qué horarios tienes para el viernes?

    Bot: (Consulta el JSON) Para el 2025-10-03 las horas disponibles son: 14:00, 15:00, 16:00. ¿Te gustaría agendar en alguno de esos horarios? Por favor, indica la hora.

    Usuario: 15:00

    Bot: (Pasa por prepararConfirmacion y luego a confirmar) Perfecto. ¿Confirmo tu cita para el 2025-10-03 a las 15:00?

    Usuario: Sí.

    Bot: ¡Genial! Tu cita ha sido agendada.

    📄 Para una lista completa y detallada de todos los casos de uso y flujos contemplados, por favor consulta la documentación en la carpeta /docs.

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
