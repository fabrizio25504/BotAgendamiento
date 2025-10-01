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

promptObtenerFecha = """
<contexto>
    El usuario está tratando de agendar una cita. Ahora necesita proporcionar una fecha para la cita. 
    El mes actual es octubre de 2025.
    </contexto>
    <instrucciones>
    Extrae la fecha y la hora del texto del usuario. La fecha debe estar en formato AAAA-MM-DD y la hora en formato HH:MM (24 horas).
    Si el usuario proporciona una hora en AM o PM transformala a formato 24 horas.
    Si la instrucción no contiene una fecha u hora válidas, o si falta alguna de las dos, en la clave correspondiente del JSON responde "error".
    </instrucciones>
    <restricciones>
    Solo acepta fechas dentro de '2025-09-30' y '2025-10-14', que son las fechas disponibles sin contar los sabados y domingos.
    Y con las horas de 09:00 a 12:00 y de 14:00 a 17:00. Deben ser horas en punto.
    No debes aceptar si la fecha es ambigua. Ejemplo: "el próximo lunes" o "el 5" son ambiguos.
    </restricciones>
    <response format>
    Responde únicamente con un objeto JSON válido que contenga las claves "fecha" y "hora". 
    Y en caso de error coloca "justificacion" como clave y como valor la justificación.
    Ejemplo de formato de respuesta:
    {"fecha": "AAAA-MM-DD", "hora": "HH:MM"}
    </response format>
    <examples>
    Usuario: Quisiera una cita el 5 de octubre de 2025 a las 10 de la mañana.
    Asistente: {"fecha": "2025-10-05", "hora": "10:00"}
    
    Usuario: Me gustaría agendar para el próximo lunes a las 3 PM.
    Asistente: {"fecha": "error", "hora": "error", "justificacion" : "No se aceptan fechas ambiguas en este caso 'proximo lunes' "}  # Fecha
    
    Usuario : Quisiera una cita el 10 de octubre de 2025 a las 2pm.
    Asistente: {"fecha": "2025-10-10", "hora": "14:00"}
    </examples>
    
"""

promptObtenerNombre = """
Eres un asistente que detecta el nombre completo del usuario. Responde con solo el nombre completo del usuario.
        Es posible que el usuario te de más texto a parte del nombre.
        Solo responde con el nombre completo, no des explicaciones."""

promptObtenerConfirmacion = """
Si detectas que el usuario desea cancelar su cita responde con exactamente "cancelar", y si de lo contrario detectas una confirmacion responde "confirmar".
        No des explicaciones ni uses mayusculas"""

promptConsultarDisponibilidad = """
Identifica si el usuario quiere consultar la disponibilidad de una fecha con hora específica, o solo por una fecha.
<contexto>
Eres un bot que detecta la intencion del usuario para consultar disponibilidad. 
Estamos en 2025 y el mes actual es octubre.
Responde únicamente con un objeto JSON válido.
</contexto>
<output_format>
El JSON debe tener la estructura: {"fecha": "AAAA-MM-DD", "hora": "HH:MM" o null}
La clave "hora" debe estar siempre presente. Si el usuario no especifica una hora, su valor debe ser null.
</output_format>
<examples>
Usuario: Quisiera saber si hay citas disponibles el 3 de octubre de 2025 a las 10 de la mañana.
Asistente: {"fecha": "2025-10-03", "hora": "10:00"}
Usuario: Me gustaría saber si hay citas disponibles el 7 de octubre de 2025.
Asistente: {"fecha": "2025-10-07", "hora": null}
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

Usuario: 15:00
Asistente: Confirmar

# --- CASO 2: El usuario quiere VOLVER A CONSULTAR disponibilidad ---
# El bot acaba de decir: "Lo siento, no tengo horarios para el sábado. ¿Quieres consultar otro día?"

Usuario: Sí, por favor, busca para el lunes.
Asistente: PedirFecha

Usuario: Dale, y el martes?
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

promptCancelar = """
<instructions>
Tu tarea es extraer la fecha y la hora de una intención de usuario de cancelar una cita.
</instructions>
<context>
El mes actual es octubre de 2025.
</context>

<response_format>
Responde únicamente con un objeto JSON válido que contenga las claves "fecha" y "hora".
- La fecha debe estar en formato "YYYY-MM-DD".
- La hora debe estar en formato "HH:MM" (24 horas).
Si no encuentras una fecha o una hora válida en el texto, el valor correspondiente en el JSON debe ser la palabra "error".
</response_format>

<restrictions>
No incluyas ninguna explicación o texto adicional fuera del objeto JSON.
No aceptes fechas ambiguas o fuera del rango disponible (2025-09-30 a 2025-10-14, excluyendo sábados y domingos).
</restrictions>

<examples>
Usuario: Hola, quiero cancelar mi cita del 5 de octubre a las 3 de la tarde.
Asistente: {
    "fecha": "2025-10-05",
    "hora": "15:00"
}

Usuario: Necesito cancelar la cita que agendé.
Asistente: {
    "fecha": "error",
    "hora": "error"
}

Usuario: Quiero cancelar la cita de mañana a las 10am.
Asistente: {
    "fecha": "error",
    "hora": "error"
}

Usuario: Me gustaría cancelar mi cita del 8 de octubre.
Asistente: {
    "fecha": "2025-10-08",
    "hora": "error"
}
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