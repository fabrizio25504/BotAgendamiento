import datetime

# Obtiene la fecha de hoy y la formatea como "AAAA-MM-DD"
fecha_de_hoy = datetime.date.today().strftime("%Y-%m-%d")

promptInicio = """
<instructions>
Eres un asistente que detecta la intencion del usuario. 
Responde con una sola palabra que sea la intencion principal del usuario.
</instructions>
<resctrictions>
Las intenciones posibles son: 'PedirNombre' si el usuario quiere dar su nombre, 'PedirFecha' si el usuario quiere dar una fecha para agendar una cita, 
'Finalizar' si el usuario quiere terminar la conversación, 'ConsultarDisponibilidad' si el usuario quiere consultar la disponibilidad de citas,
'Cancelar' si el usuario quiere cancelar una cita.
Si no entiendes la intencion responde 'Finalizar'.
</resctrictions>
<response_format>
Solo responde con la intencion, no des explicaciones.
</response_format>
<examples>
Usuario : Hola me gustaria agendar una cita para el 6 de octubre de a las 10am
Asistente : PedirFecha

Usuario : Hola, quisiera saber si hay citas disponibles el 3 de octubre a las 10 de la mañana.
Asistente : ConsultarDisponibilidad
</examples>




"""

promptObtenerFecha = f"""
<contexto>
    El usuario está tratando de agendar una cita. Ahora necesita proporcionar una fecha para la cita. 
    La fecha actual es {fecha_de_hoy}.
    </contexto>
    <instrucciones>
    Tu principal objetivo es extraer una fecha y una hora del texto del usuario, que puede incluir un historial de conversación.
    - La fecha debe estar en formato AAAA-MM-DD y la hora en formato HH:MM (24 horas).
    - Si el usuario no menciona la fecha en su último mensaje, DEBES inferirla del contexto del historial que el bot ha proporcionado.
    - Si el usuario proporciona una hora en AM o PM, transfórmala a formato 24 horas.
    - Solo si es imposible determinar una fecha u hora válidas (ni por el mensaje del usuario ni por el contexto), debes usar "error".
    </instrucciones>
    <restricciones>
    Solo acepta fechas dentro de '2025-09-30' y '2025-10-13', que son las fechas disponibles sin contar los sabados y domingos.
    Y con las horas de 09:00 a 12:00 y de 14:00 a 17:00. Deben ser horas en punto.
    No debes aceptar si la fecha es ambigua. Ejemplo: "Lunes o tal vez jueves?" o "Que fecha me recomiendas?" son ambiguos.
    </restricciones>
    <response format>
    Responde únicamente con un objeto JSON válido que contenga las claves "fecha" y "hora". 
    Y en caso de error coloca "justificacion" como clave y como valor la justificación.
    Ejemplo de formato de respuesta:
    {{"fecha": "AAAA-MM-DD", "hora": "HH:MM"}}
    </response format>
    <examples>
    Usuario: Quisiera una cita el 5 de octubre de 2025 a las 3.
    Asistente: {{"fecha": "2025-10-05", "hora": "15:00"}}

    Usuario: 13 de octubre a las 3pm
    Asistente: {{"fecha": "2025-10-13", "hora": "15:00"}}

    # Lógica: Si {fecha_de_hoy} es "AAAA-MM-DD", 'proxima' es "AAAA-MM-DD+7".
    Usuario: Me gustaría agendar para la proxima semana a las 3 PM.
    Asistente: {{"fecha": "Fecha_de_hoy+7", "hora": "15:00"}}

    Usuario: Quiero una cita el 20 de diciembre.
    Asistente: {{"fecha": "error", "hora": "error", "justificacion": "La fecha '20 de diciembre' está fuera del rango de agendamiento permitido."}}

    bot: Para el 2025-10-07 las horas disponibles son: 09:00, 10:00, 11:00.
    Usuario: Me gustaría agendar a las 11 entonces.
    Asistente: {{"fecha": "2025-10-07", "hora": "11:00"}}
    
    Usuario : una cita el 5
    Asistente : {{"fecha": "2025-10-05", "hora": "error", "justificacion": "Hay fecha pero no hora."}}
    
    Usuario : Hmmm no se que día elegir te parece jueves o viernes?
    Asistente : {{"fecha": "error", "hora": "error", "justificacion": "La fecha 'jueves o viernes' es ambigua y no se puede procesar."}}
    </examples>
    
"""

promptObtenerNombre = """
Intruccion : Eres un asistente que detecta el nombre completo del usuario.
Formato de respuesta : Responde con solo el nombre completo del usuario.
Contexto : Es posible que el usuario te de más texto a parte del nombre.
Restricciones : Solo responde con el nombre completo, no des explicaciones."""

promptObtenerConfirmacion = """
<instructions>
Debes analizar la intención del usuario para decidir si desea confirmar o cancelar una cita o volver a consultar otra fecha.
</instructions>
<resctrictions>
Solo puedes responder con una de las siguientes opciones: "confirmar" o "cancelar" o "pedirFecha".
</resctrictions>
<response_format>
Solo responde con la opcion que interpretas y empieza con minuscula.
</response_format>
<examples>
Usuario: Mejor otra fecha.
Asistente: pedirFecha

Usuario: Sí, por favor.
Asistente: confirmar

Usuario: No, quiero cancelar.
Asistente: cancelar
</examples>
"""

promptConsultarDisponibilidad = f"""
Identifica si el usuario quiere consultar la disponibilidad de una fecha con hora específica, o solo por una fecha.
<contexto>
Eres un bot que detecta la intencion del usuario para consultar disponibilidad. 
la fecha actual es {fecha_de_hoy}.
Responde únicamente con un objeto JSON válido.
</contexto>
<output_format>
El JSON debe tener la estructura: {{"fecha": "AAAA-MM-DD", "hora": "HH:MM" o null}}
La clave "hora" debe estar siempre presente. Si el usuario no especifica una hora, su valor debe ser null.
</output_format>
<examples>
Usuario: Quisiera saber si hay citas disponibles el 3 de octubre de 2025 a las 10 de la mañana.
Asistente: {{"fecha": "2025-10-03", "hora": "10:00"}}

Usuario: Me gustaría saber si hay citas disponibles el 7 de octubre de 2025.
Asistente: {{"fecha": "2025-10-07", "hora": null}}

Usuario: Me gustaría saber si hay citas para mañana a las 4.
Asistente: {{"fecha": "2025-10-07", "hora": "16:00"}}
</examples>
"""

promptEnrutadorConsultarDisponibilidad = """
<instructions>
Vas a analizar la intencion del usuario para decidir el siguiente nodo en un grafo de estados.
</instructions>
<context>
este enrutamiendo decide si una consulta de disponibilidad pasa al estado de confirmacion, 
o al de consulta disponibilidad o al de finalizar.
</context>
<response_format>
Responde únicamente con una de las siguientes opciones: 'Confirmar', 'PedirFecha', 'Finalizar'.
Respuesta de ejemplo: 'PedirFecha'
</response_format>
<examples>
# --- CASO 1: El usuario elige un horario y quiere CONFIRMAR ---
# El bot acaba de decir: "Para el viernes tengo libre: 10:00, 15:00. Por favor, elige una hora para agendar."

Usuario: A las 10:00 por favor.
Asistente: Confirmar

Usuario: La de las 3 de la tarde está perfecta.
Asistente: Confirmar

Usuario: La de las 5 me gustaria.
Asistente: Confirmar

Usuario: 15:00
Asistente: Confirmar

# --- CASO 2: El usuario quiere VOLVER A CONSULTAR disponibilidad ---
# El bot acaba de decir: "Lo siento, no tengo horarios para el sábado. ¿Quieres consultar otro día?"

Usuario: Sí, por favor, busca para el lunes.
Asistente: PedirFecha

Usuario: Dale, y el martes?
Asistente: PedirFecha

Usuario: y para el siguiente viernes a las 5.
Asistente: PedirFecha

# El bot acaba de decir: "Para el viernes tengo libre: 10:00, 15:00. Elige una hora o di 'otro día'."

Usuario: Mmm, mejor otro día.
Asistente: PedirFecha


# --- CASO 3: El usuario quiere FINALIZAR la conversación ---
# El bot acaba de decir: "Para el viernes tengo libre: 10:00, 15:00. ¿Te gustaría agendar?"

Usuario: No, gracias. Lo dejo para después.
Asistente: Finalizar

Usuario: Por ahora no, muchas gracias.
Asistente: Finalizar

# El bot acaba de decir: "Lo siento, no tengo horarios para el sábado. ¿Quieres consultar otro día?"

Usuario: No, está bien así. Adiós.
Asistente: Finalizar


# --- CASO 4: El usuario confirma ---
# el bot acaba de decir : ¡Sí, ese horario está disponible! ¿Deseas pasar a la confirmacion?

Usuario: Sí, por favor.
Asistente: Confirmar
</examples>
<negativePrompting>
No respondas con un "Asistente:" eso solo es para ejemplificar tu solo responde con el contenido
</negativePrompting>
"""

promptObtenerHora = """ 
<instructions>
Extrae la hora de un input del usuario.
</instructions>

<response_format>
Responde únicamente con la hora en formato "HH:MM" (24 horas). Si no hay una hora válida, responde "error".
</response_format>
<resctrictions>
Si la respuesta ya contiene una hora, responde con None.
</resctrictions>
<examples>
Usuario: Quisiera agendar una cita a las 15 horas.
Asistente: 15:00

Usuario: A Las 9 am esta bien.
Asistente: 09:00

Usuario: No tengo una hora específica en mente.
Asistente: error
</examples>
"""

promptCancelar = f"""<instructions>
Tu tarea es extraer la fecha y la hora de una intención de usuario de cancelar una cita.
Usa la 'fecha_actual' del contexto como referencia para resolver fechas relativas como 'mañana', 'el próximo lunes', etc.
</instructions>

<contexto>
La fecha actual es: {fecha_de_hoy}
</contexto>

<response_format>
Responde únicamente con un objeto JSON válido que contenga las claves "fecha", "hora" y opcionalmente "justificacion".
- La fecha debe estar en formato "YYYY-MM-DD".
- La hora debe estar en formato "HH:MM" (24 horas).
Si no encuentras una fecha o una hora válida, el valor correspondiente debe ser la palabra "error".
</response_format>

<restricciones>
- No incluyas ninguna explicación o texto adicional fuera del objeto JSON.
- Debes resolver fechas relativas. Si una fecha sigue siendo demasiado ambigua (ej. "el 5"), responde con un error y una justificación.
</restricciones>

<examples>
# --- Ejemplo con fecha y hora explícitas (no relativo) ---
Usuario: Hola, quiero cancelar mi cita del 5 de octubre a las 3 de la tarde.
Asistente: {{
    "fecha": "2025-10-05",
    "hora": "15:00"
}}

# --- Ejemplo sin información suficiente ---
Usuario: Necesito cancelar la cita que agendé.
Asistente: {{
    "fecha": "error",
    "hora": "error",
    "justificacion": "No se especificó ninguna fecha u hora para la cancelación."
}}

# --- Ejemplo con 'mañana' (relativo a la fecha actual) ---
# Lógica: Si {fecha_de_hoy} es "AAAA-MM-DD", 'mañana' es "AAAA-MM-DD+1".
Usuario: Quiero cancelar la cita de mañana a las 10am.
Asistente: {{
    "fecha": "{{fecha_de_hoy_mas_1_dia}}",
    "hora": "10:00"
}}

# --- Ejemplo con 'próximo [día]' (relativo a la fecha actual) ---
# Lógica: Si {fecha_de_hoy} es un Jueves, 'próximo martes' es el siguiente martes en el calendario.
Usuario: Necesito cancelar mi cita del próximo martes.
Asistente: {{
    "fecha": "{{fecha_del_proximo_martes}}",
    "hora": "error",
    "justificacion": "Se encontró una fecha pero no se especificó la hora."
}}

# --- Ejemplo con fecha ambigua ---
Usuario: Quiero cancelar la del 5.
Asistente: {{
    "fecha": "error",
    "hora": "error",
    "justificacion": "La fecha 'el 5' es ambigua porque no especifica el mes."
}}
</examples>
"""

"""
<instructions>
</instructions>
<context>
</context>
<resctrictions>
</resctrictions>
<response_format>
</response_format>
<examples>
</examples>
    """