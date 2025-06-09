# Agente de Agendamiento con LangGraph

Este proyecto utiliza [LangGraph](https://github.com/langchain-ai/langgraph) para construir un agente conversacional que permite observar el flujo de conversación mediante una interfaz gráfica.

## 🚀 Requisitos

*   Python 3.11
*   Cuenta en Google Cloud Platform (para generar una API key)
*   Clave de API `GOOGLE_API_KEY`

## ⚙️ Instalación

**Crea un entorno virtual con Python 3.11 (opcional conda)**:

```
conda create -n langgraph_env python==3.11
conda activate langgraph_env
```

**Instala las dependencias**:

```
pip install -r requirements.txt
```

**Configura tu clave de API de Google y agregala al archivo .env**:

```
GOOGLE_API_KEY="tu_clave_api"
```

**Ejecución del flujo conversacional**  
Una vez configurado el entorno, puedes observar el flujo del grafo de conversación con el siguiente comando:

```
langgraph dev
```

Esto abrirá una interfaz local donde podrás interactuar con el agente y ver la evolución del estado dentro del grafo.