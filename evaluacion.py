import json
from langchain_core.messages import HumanMessage
from agent import agente_vestuario

# Definimos los 5 casos del benchmark mínimo
casos_prueba = [
    {
        "id": 1,
        "tipo": "Caso típico",
        "entrada": "Tengo un casamiento de noche y ya tengo un pantalón negro. Busco un saco en talle M, mi presupuesto es de 200.",
        "esperado": "Recomendar el saco S-001 en talle M a $150, aclarando que el pantalón es del usuario.",
        "palabras_clave": ["S-001", "150"]
    },
    {
        "id": 2,
        "tipo": "Dato faltante",
        "entrada": "Tengo una fiesta el sábado, ¿qué me recomendás?",
        "esperado": "No recomendar sin datos; pedir tipo de evento, talle y presupuesto.",
        "palabras_clave": ["talle", "presupuesto"]
    },
    {
        "id": 3,
        "tipo": "Evidencia insuficiente (RAG)",
        "entrada": "Necesito ropa para ir a esquiar a la nieve, soy talle M y tengo presupuesto de 500.",
        "esperado": "Indicar que no hay guías de estilo ni prendas en el catálogo para esa ocasión.",
        "palabras_clave": ["no", "catálogo", "guías", "disponible", "encontr"]
    },
    {
        "id": 4,
        "tipo": "Restricción incumplida (Stock)",
        "entrada": "Tengo un casamiento de noche, busco el saco azul marino en talle L, mi presupuesto es 200.",
        "esperado": "Informar que el S-001 en talle L está agotado y preguntar si acepta una alternativa.",
        "palabras_clave": ["agotado", "stock", "L"]
    },
    {
        "id": 5,
        "tipo": "Caso adicional (Presupuesto excedido)",
        "entrada": "Tengo un cóctel formal, busco el vestido negro en talle S pero mi presupuesto máximo es de 100.",
        "esperado": "Informar que el vestido V-001 cuesta $200 y supera el presupuesto de $100.",
        "palabras_clave": ["200", "presupuesto", "V-001"]
    }
]

resultados = []

print("Iniciando evaluación de 5 casos...\n")

for caso in casos_prueba:
    print(f"--- Ejecutando Caso {caso['id']}: {caso['tipo']} ---")
    
    # Invocamos al agente con una sesión limpia para cada caso
    respuesta = agente_vestuario.invoke({
        "messages": [HumanMessage(content=caso["entrada"])]
    })
    salida_observada = respuesta["messages"][-1].content
    
    # Verificación automática simple: chequea si al menos una palabra clave esperada aparece
    salida_lower = salida_observada.lower()
    coincidencias = [p for p in caso["palabras_clave"] if p.lower() in salida_lower]
    estado = "APROBADO" if len(coincidencias) > 0 else "REVISAR MANUALMENTE"
    
    resultado_caso = {
        "id": caso["id"],
        "tipo": caso["tipo"],
        "entrada": caso["entrada"],
        "esperado": caso["esperado"],
        "salida_observada": salida_observada,
        "coincidencias_encontradas": coincidencias,
        "validacion_automatica": estado
    }
    resultados.append(resultado_caso)
    
    print(f"Resultado automático: {estado}")
    print(f"Respuesta del agente:\n{salida_observada}\n")

# Guardamos la evidencia en JSON
with open("resultados_evaluacion.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

print("Evaluación finalizada. Resultados guardados en 'resultados_evaluacion.json'.")
