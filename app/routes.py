from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import buscar_resposta

router = APIRouter()

class PerguntaRequest(BaseModel):
    session_id: str
    ask:   str

class RespostaResponse(BaseModel):
    ans: str

@router.post("/perguntar", response_model=RespostaResponse)
async def perguntar(body: PerguntaRequest):
    if not body.ask.strip():
        raise HTTPException(status_code=400, detail="A pergunta nao pode ser vazia!")

    if not body.session_id.strip():
        raise HTTPException(status_code=400, detail="O ID da sessao nao pode estar vazio!")

    ans = await buscar_resposta(body.session_id, body.ask)

    if ans is None:
        raise HTTPException(status_code=404, detail="Não encontrei informações suficientes na base")

    return RespostaResponse(ans=ans)