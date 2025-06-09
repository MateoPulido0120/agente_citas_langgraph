from typing import Annotated
import re
from typing_extensions import TypedDict
import json
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage



load_dotenv()

os.environ["GOOGLE_API_KEY"]

llm = init_chat_model("google_genai:gemini-2.0-flash")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    states_conversation: dict
    states_completed: dict


graph_builder = StateGraph(State)


def validator_states_conversation(state: State):
    system_message = SystemMessage(content=""" Valida si el mensjae de "HUMAN" infiere ejecutar alguna (SOLO UNA) de las siguientes acciones:
                                            1. Mensaje de bienvenida.
                                            2. Identificacion de solicitud de cita medica.
                                            3. Tipo y numero de documento.
                                            4. EPS (Entidad promotora de salud) a la que pertenece y especilidad medica requerida.
                                            5. Mensaje de despedida.
                                            6. Mensaje con contexto totalmente diferente.
                                   
                                   Itenfica segun el ultimo mensaje de "HUMAN", retorna tu respuesta como esquema json:
                                   {{
                                   "bienvenida": bool,
                                   "solicitud_cita": bool,
                                   "tipo_numero_doc": bool,
                                   "eps_especialidad": bool,
                                   "despedida": bool,
                                   "otro": bool,
                                   }}
                                   """)

    response = llm.invoke([system_message] + state["messages"])

    try:
        # Extrae el contenido textual de la respuesta
        content = response.content if hasattr(response, "content") else response[0]["content"]

        # Usa expresión regular para extraer el primer bloque JSON del texto
        match = re.search(r"\{.*?\}", content, re.DOTALL)

        if match:
            json_text = match.group(0)
            data = json.loads(json_text)
        else:
            raise ValueError("No se encontró un bloque JSON válido en la respuesta.")
        
        return {
            "messages": state["messages"] + [response],
            "states_conversation": data,
            "states_completed": {}
        }

    except Exception as e:
        print("Error al parsear JSON:", e)
        return {
            "messages": state["messages"] + [response],
            "states_conversation": {},
            "states_completed": {}
        }

def check_state_completion(state: State):

    if state["states_conversation"]["bienvenida"]:
        return "bienvenida"
    elif state["states_conversation"]["solicitud_cita"]:
        return "solicitud_cita"
    elif state["states_conversation"]["tipo_numero_doc"]:
        return "tipo_numero_doc"
    elif state["states_conversation"]["eps_especialidad"]:
        return "eps_especialidad"
    
    return "despedida"


def welcome_message(state: State):
    state["states_completed"]["bienvenida"] = True

    system_message = SystemMessage(content="Eres un agente de una entidad de salud X, genera un mensaje de bienvendida al usaurio e informa que tu objetivo es ayudarlo con agendamiento de citas medicas")

    response = llm.invoke([system_message] + state["messages"])

    return {
        "messages": state["messages"] + [response],
        "states_conversation": state["states_conversation"],
        "states_completed": state["states_completed"]
    }


def farewell_message(state: State):
    state["states_completed"]["despedida"] = True

    system_message = SystemMessage(content="Genera un mensaje de despedida agradeciendo al usaurio por su interaccion")

    response = llm.invoke([system_message] + state["messages"])

    return {
        "messages": state["messages"] + [response],
        "states_conversation": state["states_conversation"],
        "states_completed": state["states_completed"]
    }


graph_builder.add_node("validator_states_conversation", validator_states_conversation)
graph_builder.add_node("welcome_message", welcome_message)
graph_builder.add_node("farewell_message", farewell_message)


graph_builder.add_conditional_edges(
    "validator_states_conversation",
    check_state_completion,
    {
        "bienvenida": "welcome_message",
        "solicitud_cita": END,
        "tipo_numero_doc": END,
        "eps_especialidad": END,
        "despedida": "farewell_message"
    }
)


graph_builder.add_edge(START, "validator_states_conversation")
graph_builder.add_edge("welcome_message", END)
graph_builder.add_edge("farewell_message", END)


graph = graph_builder.compile()



