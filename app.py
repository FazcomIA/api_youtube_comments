from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader
from typing import List

# Inicializar o aplicativo FastAPI
app = FastAPI(title="YouTube Comments API", description="API para extrair comentários de vídeos do YouTube")

# Configurar o esquema de autenticação por token
security = HTTPBearer()
TOKEN = "Y2FuYWxmYXpjb21JQQ=="  # Token único fornecido


# Função para verificar o token
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")
    return credentials.credentials


# Modelo para validar a entrada
class CommentRequest(BaseModel):
    video_url: str
    max_comments: int


# Modelo para estruturar a saída
class Comment(BaseModel):
    author: str
    comment: str
    published_at: str


# Endpoint para obter comentários
@app.post("/comments", response_model=List[Comment])
async def get_comments(request: CommentRequest, token: str = Depends(verify_token)):
    try:
        # Validar max_comments
        if request.max_comments < 1:
            raise HTTPException(status_code=400, detail="max_comments deve ser maior que 0")

        # Inicializar o downloader
        downloader = YoutubeCommentDownloader()

        # Baixar comentários
        comments = downloader.get_comments_from_url(request.video_url, sort_by=1)  # 1 = mais recentes primeiro

        # Coletar comentários até o limite
        comment_list = []
        for comment in islice(comments, request.max_comments):
            comment_list.append({
                "author": comment["author"],
                "comment": comment["text"],
                "published_at": comment["time"]
            })

        if not comment_list:
            raise HTTPException(status_code=404, detail="Nenhum comentário encontrado")

        return comment_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a requisição: {str(e)}")


# Endpoint raiz
@app.get("/")
async def root():
    return {"message": "Bem-vindo à YouTube Comments API. Use o endpoint /comments com um token válido."}