import openai
import os
import requests

# Configura tu API Key de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# ID de tu asistente creado en OpenAI
ASSISTANT_ID = "asst_PeHr9lOZhm96n5nRLmBT4eEjG"  # Cambialo si cambia el ID

# Define función para llamar al asistente
def llamar_asistente(mensaje_usuario):
    client = openai.OpenAI()

    # 1. Crear un hilo de conversación
    thread = client.beta.threads.create()

    # 2. Enviar mensaje del usuario al hilo
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=mensaje_usuario
    )

    # 3. Ejecutar el asistente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    # 4. Esperar que termine
    while True:
        estado = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if estado.status == "completed":
            break

    # 5. Leer respuesta
    mensajes = client.beta.threads.messages.list(thread_id=thread.id)
    for m in mensajes.data:
        for contenido in m.content:
            print("💬", contenido.text.value)

# === Ejecución directa ===
if __name__ == "__main__":
    moneda = input("¿Qué moneda querés consultar? (Ej: BTC, ETH, SOL):\n> ")
    llamar_asistente(f"¿Cuál es el precio actual de {moneda}?")