from pymongo import MongoClient
from datetime import datetime, timezone

# Conecta ao MongoDB local
cliente = MongoClient("mongodb://localhost:27017")
db      = cliente["chatbot"]
colecao = db["usuarios"]

def save_resume(session_id: str, resumo: str):
    """
    Salva ou atualiza o resumo de longo prazo do usuário.
    upsert=True: cria o documento se não existir.
    """
    colecao.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "resumo": resumo,
                "atualizado_em": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )

def search_resume(session_id: str) -> str | None:
    """
    Retorna o resumo salvo do usuário, ou None se for primeira vez.
    """
    doc = colecao.find_one({"session_id": session_id})
    if doc:
        return doc.get("resumo")
    return None

def generate_resume_session(historico: list[dict]) -> str:
    """
    Gera um resumo simples do histórico para salvar no MongoDB.
    Em produção você pode chamar o LLM para resumir.
    """
    if not historico:
        return ""
    perguntas = [m["conteudo"] for m in historico if m["role"] == "human"]
    return f"Usuário fez {len(perguntas)} pergunta(s). Última: {perguntas[-1]}"