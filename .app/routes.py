from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import buscar_resposta

router = APIRouter()

class PerguntaRequest(BaseModel):
    session_id: str
    pergunta:   str

class RespostaResponse(BaseModel):
    resposta: str

@router.post("/perguntar", response_model=RespostaResponse)
async def perguntar(body: PerguntaRequest):
    if not body.pergunta.strip():
        raise HTTPException(status_code=400, detail="A pergunta nao pode ser vazia!")

    if not body.session_id.strip():
        raise HTTPException(status_code=400, detail="O ID da sessao nao pode estar vazio!")

    resposta = await buscar_resposta(body.session_id, body.pergunta)

    if resposta is None:
        raise HTTPException(status_code=404, detail="Não encontrei informações suficientes na base")

    return RespostaResponse(resposta=resposta)