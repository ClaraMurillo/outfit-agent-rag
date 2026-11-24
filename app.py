import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import agente_vestuario

st.title("Asistente de Vestuario 👔👗")
st.write("Dime qué evento tienes, tu talle y tu presupuesto.")

# Inicializar el historial de chat en la memoria de la interfaz
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar los mensajes anteriores en pantalla
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Caja de texto para que el usuario escriba
if prompt := st.chat_input("Ej: Tengo una boda de noche, soy talle M y mi presupuesto es $200"):
    
    # 1. Mostrar lo que escribió el usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Procesar con el Agente
    with st.chat_message("assistant"):
        with st.spinner("Revisando reglas de estilo e inventario..."):
            
            # Convertir el historial de Streamlit al formato que entiende LangChain
            historial_langchain = []
            for m in st.session_state.messages:
                if m["role"] == "user":
                    historial_langchain.append(HumanMessage(content=m["content"]))
                else:
                    historial_langchain.append(AIMessage(content=m["content"]))
            
            # Ejecutar nuestro grafo de LangGraph
            resultado = agente_vestuario.invoke({"messages": historial_langchain})
            
            # Extraer la última respuesta del bot
            respuesta_bot = resultado["messages"][-1].content
            st.markdown(respuesta_bot)
            
    # Guardar la respuesta en el historial
    st.session_state.messages.append({"role": "assistant", "content": respuesta_bot})
