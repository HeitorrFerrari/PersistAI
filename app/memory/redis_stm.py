import redis
import json

cliente = redis.Redis(host="localhost", port=6379, decode_responses=True)

TTL_SEGUNDOS = 60 * 60 * 2
MAX_MENSAGENS = 10  

def salvar_mensagem(session_id: str, role: str, conteudo: str):
    """
    Salva uma mensagem no histórico da sessão.
    role: 'human' ou 'ai'
    """
    chave = f"historico:{session_id}"
    mensagem = json.dumps({"role": role, "conteudo": conteudo})

    cliente.rpush(chave, mensagem)

    cliente.ltrim(chave, -MAX_MENSAGENS, -1)

    cliente.expire(chave, TTL_SEGUNDOS)

def buscar_historico(session_id: str) -> list[dict]:
    """
    Retorna o histórico da sessão como lista de dicts.
    Retorna lista vazia se não houver histórico.
    """
    chave = f"historico:{session_id}"
    mensagens = cliente.lrange(chave, 0, -1)
    return [json.loads(m) for m in mensagens]

def formatar_historico(historico: list[dict]) -> str:
    """
    Formata o histórico para injetar no contexto do LLM.
    """
    if not historico:
        return ""
    linhas = []
    for msg in historico:
        prefixo = "Usuário" if msg["role"] == "human" else "Assistente"
        linhas.append(f"{prefixo}: {msg['conteudo']}")
    return "\n".join(linhas)