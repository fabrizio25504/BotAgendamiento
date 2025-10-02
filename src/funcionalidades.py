import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError 
from state import AgentState
import json
import datetime
import random

def obtenerModelo():
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    return client

def invoke_model( prompt: str, system: str) -> str:
    client = obtenerModelo()
    try:
        response = client.converse(
            modelId="us.amazon.nova-lite-v1:0",
            messages = [{
                "role": "user",
                "content": [{"text":prompt}]
            }],
            system = [{"text" : system}],
            inferenceConfig = {
                "maxTokens": 150,
                "temperature": 0.0,
            }
        )
        return response["output"]["message"]["content"][0]["text"]
    except ClientError as e:
        print(f"Error invoking model: {e}")
        return "Error"


def disponibilidadTotal() :
    with open('disponibilidad.json', 'r', encoding='utf-8') as f:
        jsonFormated = json.load(f)
        #print(jsonFormated)
        return jsonFormated
    
def obtener_horarios_disponibles(fecha: str, disponibilidad_total: dict) -> list[str]:
    """
    Busca en el diccionario de disponibilidad y devuelve una lista con las HORAS disponibles.
    Responsabilidad: Procesar datos. Es el "Chef".
    """
    horarios_del_dia = disponibilidad_total.get(fecha, [])
    #print("horarios del dia : ", horarios_del_dia)
    # Devuelve una lista simple de strings con las horas, ej: ["10:00", "11:00"]
    horas_libres = [
        item["hora"] for item in horarios_del_dia if item.get("disponible")
    ]
    #print("horas libres : ", horas_libres)
    return horas_libres

def confirmarHora(hora, fecha, disponibilidad):
    fechas_disponibles = disponibilidad.get(fecha)
    
    horas_disponibles = [item for item in fechas_disponibles if item['disponible']]
    
    for item in horas_disponibles:
        if item['hora'] == hora:
            print(f"La hora {hora} está disponible para la fecha {fecha}.")
            return True
    
    print(f"La hora {hora} no está disponible para la fecha {fecha}.")
    return False


def parsearFechaHora(input, state):
    input = input.replace("```", '').replace("json", '').strip()
    #print("pasando por parser" + input)
    try:
        data = json.loads(input)
        state["fecha"] = data.get("fecha")
        state["hora"] = data.get("hora")

    except json.JSONDecodeError:
        state["fecha"] = "error"
        state["hora"] = "error"

    return state


def cargar_disponibilidad(ruta_archivo="disponibilidad.json"):
    """Carga los datos de disponibilidad desde un archivo JSON.
    Usa disponibilidadTotal() para evitar duplicación de código."""
    return disponibilidadTotal()

def guardar_disponibilidad(datos, ruta_archivo="disponibilidad.json"):
    """Guarda los datos de disponibilidad en un archivo JSON."""
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)

def setearDisponibilidad(fecha, hora, disponible: bool, disponibilidad):
    """Modifica la disponibilidad en memoria. Retorna True si tuvo éxito."""
    if fecha in disponibilidad:
        horarios_del_dia = disponibilidad[fecha]
        # Buscar el horario específico en la lista
        for horario_obj in horarios_del_dia:
            if horario_obj.get('hora') == hora:
                horario_obj['disponible'] = disponible
                return True
    return False

# --- La nueva función "orquestadora" que lo hace todo ---
def actualizar_y_guardar_disponibilidad(fecha: str, hora: str, disponible: bool, ruta_archivo="disponibilidad.json"):
    """
    Función de alto nivel que orquesta el ciclo completo:
    1. Carga los datos del JSON.
    2. Intenta modificar la disponibilidad.
    3. Si tiene éxito, guarda los cambios de vuelta en el JSON.
    Retorna True si el cambio fue guardado, False en caso contrario.
    """
    # Paso 1: Leer
    disponibilidad_actual = cargar_disponibilidad(ruta_archivo)
    
    # Paso 2: Modificar
    exito_modificacion = setearDisponibilidad(fecha, hora, disponible, disponibilidad_actual)
    
    # Paso 3: Escribir (solo si hubo cambios)
    if exito_modificacion:
        guardar_disponibilidad(disponibilidad_actual, ruta_archivo)
        #print(f"Cambio guardado en {ruta_archivo}: {fecha} a las {hora} ahora está {'disponible' if disponible else 'no disponible'}.")
        return True
    else:
        #print(f"No se pudo actualizar: El horario {fecha} a las {hora} no fue encontrado.")
        return False



def generar_json_disponibilidad():
    """
    Genera un archivo JSON con la disponibilidad para las próximas 2 semanas,
    excluyendo los fines de semana y asignando disponibilidad aleatoria.
    """
    # --- Configuración ---
    hoy = datetime.date.today()
    fecha_inicio = hoy + datetime.timedelta(days=1)
    dias_a_generar = 14
    
    # Horarios de trabajo durante la semana
    horarios_semana = [
        "09:00", "10:00", "11:00", "12:00",
        "14:00", "15:00", "16:00", "17:00"
    ]
    
    disponibilidad_total = {}

    print("Generando disponibilidad para las próximas 2 semanas...")

    # --- Lógica de Generación ---
    for i in range(dias_a_generar):
        fecha_actual = fecha_inicio + datetime.timedelta(days=i)
        
        # weekday() -> Lunes=0, Martes=1, ..., Sábado=5, Domingo=6
        dia_de_la_semana = fecha_actual.weekday()
        
        # Convertimos la fecha a formato de texto 'YYYY-MM-DD' para la clave del JSON
        clave_fecha = fecha_actual.strftime("%Y-%m-%d")
        
        horarios_del_dia = []
        
        # Si es un día de semana (Lunes a Viernes)
        if dia_de_la_semana < 5:
            for hora in horarios_semana:
                # Asignamos disponibilidad aleatoria (70% de probabilidad de estar disponible)
                esta_disponible = random.random() < 0.7 
                horarios_del_dia.append({"hora": hora, "disponible": esta_disponible})
        # Si es fin de semana, la lista de horarios queda vacía (sin disponibilidad)
        else:
            print(f"  -> {clave_fecha} es fin de semana, no se asignan horarios.")

        disponibilidad_total[clave_fecha] = horarios_del_dia
        
    # --- Creación del Archivo ---
    nombre_archivo = "disponibilidad.json"
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        # indent=2 hace que el archivo JSON sea legible para humanos
        json.dump(disponibilidad_total, f, ensure_ascii=False, indent=2)
        
    print(f"\n✅ ¡Archivo '{nombre_archivo}' generado con éxito!")

# --- Ejecutar el script ---
if __name__ == "__main__":
    #generar_json_disponibilidad()
    #disponibilidadTotal()
    #print(obtener_horarios_disponibles("2025-10-02", disponibilidadTotal()))
    actualizar_y_guardar_disponibilidad("2025-10-02", "16:00", True, "disponibilidad.json")