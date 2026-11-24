import os
from typing import Annotated
from typing_extensions import TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools import tools

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOllama(
    model="qwen2.5:latest",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)

# Creamos las instrucciones estrictas para el bot
instrucciones = SystemMessage(content="""Eres un asistente experto en moda. 
Reglas obligatorias para usar tus herramientas:
1. SIEMPRE usa primero la herramienta 'buscar_estilo' para descubrir los códigos ID de las prendas (ejemplo: C-001, S-001).
2. Cuando uses 'consultar_inventario', el parámetro id_producto DEBE ser el código exacto (ej: C-001), NUNCA el nombre de la prenda.
3. Si el usuario te pide un talle o presupuesto nuevo, vuelve a usar 'consultar_inventario' con el código ID para verificar.
4. NUNCA recomiendes un talle distinto al que pidió el usuario sin avisarle primero que su talle está agotado y preguntarle si acepta el cambio.
""")

def chatbot(state: State):
    # Le pasamos las instrucciones al modelo antes del historial de chat
    mensajes = [instrucciones] + state["messages"]
    response = llm_with_tools.invoke(mensajes)
    return {"messages": [response]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

agente_vestuario = graph_builder.compile()


