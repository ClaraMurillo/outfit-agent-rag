import sqlite3
from langchain_core.tools import tool
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
# --- 1. Inicialización del RAG ---
def inicializar_rag():
    # Cargamos el texto simulado que creaste en el paso anterior
    loader = TextLoader("data/guias_estilo.txt", encoding="utf-8")
    docs = loader.load()
    
    # Dividimos el texto en fragmentos (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)
    
    # Vectorizamos y guardamos en una base Chroma local
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory="./data/chroma_db"
    )
    return vectorstore.as_retriever(search_kwargs={"k": 2})

retriever = inicializar_rag()

# --- 2. Herramientas para el Agente ---

@tool
def buscar_estilo(query: str) -> str:
    """Útil para buscar consejos de estilo y códigos de prendas apropiadas para un evento (ej. casamiento, cóctel)."""
    docs = retriever.invoke(query)
    if not docs:
        return "No se encontraron guías de estilo para esta consulta."
    return "\n".join([d.page_content for d in docs])

@tool
def consultar_inventario(id_producto: str, talle: str, presupuesto_maximo: float) -> str:
    """Verifica el stock, el talle y el precio de un producto en la base de datos SQL."""
    conn = sqlite3.connect("data/catalogo.db")
    cursor = conn.cursor()
    
    # El talle debe estar en mayúsculas (S, M, L) según nuestra DB
    talle = talle.upper()
    
    cursor.execute('''
        SELECT precio, stock FROM inventario 
        WHERE id_producto = ? AND talle = ?
    ''', (id_producto, talle))
    
    resultado = cursor.fetchone()
    conn.close()
    
    if not resultado:
        return f"El producto {id_producto} no existe o no se fabrica en talle {talle}."
        
    precio, stock = resultado
    
    if stock <= 0:
        return f"RESTRICCIÓN INCUMPLIDA: El producto {id_producto} en talle {talle} está AGOTADO."
    if presupuesto_maximo > 0 and precio > presupuesto_maximo:
        return f"RESTRICCIÓN INCUMPLIDA: El producto {id_producto} cuesta ${precio}, superando el presupuesto de ${presupuesto_maximo}."
        
    return f"VIABLE: El producto {id_producto} en talle {talle} está disponible. Cuesta ${precio}. Stock: {stock} unidades."

# Lista de herramientas para pasárselas a LangGraph en el siguiente paso
tools = [buscar_estilo, consultar_inventario]
