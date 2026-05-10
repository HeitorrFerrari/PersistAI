from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from memory.redis_stm import salvar_mensagem, buscar_historico, formatar_historico
from memory.mongo_ltm import buscar_resumo, salvar_resumo, gerar_resumo_da_sessao

load_dotenv()

QDRANT_URL  = "http://localhost:6333"
COLLECTION  = "docs"
THRESHOLD   = 0.7

PROMPT_TEMPLATE = """
Você é um assistente prestativo. Responda com base nas informações fornecidas.

{ltm}

{stm}

Informações relevantes do documento:
{rag}

Se não encontrar a resposta nas informações, diga: "Não sei te responder isso."

Pergunta: {pergunta}
"""

async def buscar_resposta(session_id: str, pergunta: str) -> str | None:

    # 1. LTM — resumo de sessões anteriores (MongoDB)
    resumo_anterior = buscar_resumo(session_id)
    ltm = f"Contexto anterior do usuário:\n{resumo_anterior}" if resumo_anterior else ""

    # 2. STM — histórico da sessão atual (Redis)
    historico = buscar_historico(session_id)
    stm = f"Histórico desta conversa:\n{formatar_historico(historico)}" if historico else ""

    # 3. RAG — busca semântica no Qdrant
    embeddings = OpenAIEmbeddings()
    db = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        collection_name=COLLECTION,
    )
    resultados = db.similarity_search_with_relevance_scores(pergunta)

    if not resultados or resultados[0][1] < THRESHOLD:
        return None

    rag = "\n\n-----\n\n".join(r[0].page_content for r in resultados)

    # 4. Montar prompt e chamar LLM
    prompt    = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    mensagens = prompt.invoke({"ltm": ltm, "stm": stm, "rag": rag, "pergunta": pergunta})
    modelo    = ChatOpenAI(model="gpt-3.5-turbo")
    resposta  = modelo.invoke(mensagens)
    conteudo  = resposta.content

    # 5. Salvar interação no Redis (STM)
    salvar_mensagem(session_id, "human", pergunta)
    salvar_mensagem(session_id, "ai", conteudo)

    # 6. Atualizar resumo no MongoDB (LTM)
    historico_atualizado = buscar_historico(session_id)
    resumo = gerar_resumo_da_sessao(historico_atualizado)
    salvar_resumo(session_id, resumo)

    return conteudo