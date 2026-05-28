from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import whisper
import ollama
import chromadb
from sentence_transformers import SentenceTransformer
from rich.console import Console
import tempfile
import os

app = FastAPI(title="Smart Triage - Triagem Inteligente para Call Centers")
console = Console()

# Inicializa modelos e banco vetorial
modelo_embeddings = SentenceTransformer("all-MiniLM-L6-v2")
cliente_chroma = chromadb.Client()
colecao = cliente_chroma.get_or_create_collection("base_conhecimento")

# Modelo Whisper para transcrição de áudio
modelo_whisper = whisper.load_model("base")


def transcrever_audio(caminho_arquivo: str) -> str:
    # Transcreve áudio para texto usando Whisper
    resultado = modelo_whisper.transcribe(caminho_arquivo)
    return resultado["text"]


def classificar_intencao(texto: str) -> str:
    # Envia o texto ao Llama via Ollama e retorna a categoria de intenção
    resposta = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um classificador de intenções para call center. "
                    "Classifique a mensagem em uma das categorias: "
                    "CANCELAMENTO, SUPORTE_TECNICO, COBRANCA, INFORMACAO, RECLAMACAO, OUTROS. "
                    "Responda apenas com a categoria, sem explicações."
                ),
            },
            {"role": "user", "content": texto},
        ],
    )
    return resposta["message"]["content"].strip()


def extrair_problema(texto: str) -> str:
    # Resume o problema central relatado pelo usuário em uma frase curta
    resposta = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extraia em uma frase curta e objetiva o problema central relatado pelo usuário."
                ),
            },
            {"role": "user", "content": texto},
        ],
    )
    return resposta["message"]["content"].strip()


def buscar_resolucao(problema: str) -> dict:
    # Gera embedding do problema e busca a resolução mais próxima no ChromaDB
    embedding = modelo_embeddings.encode(problema).tolist()
    resultados = colecao.query(query_embeddings=[embedding], n_results=1)

    if resultados["documents"] and resultados["documents"][0]:
        return {
            "resolucao": resultados["documents"][0][0],
            "base_consultada": resultados["metadatas"][0][0].get("fonte", "base_conhecimento"),
        }

    return {
        "resolucao": "Nenhuma resolução encontrada na base de conhecimento.",
        "base_consultada": "base_conhecimento",
    }


@app.post("/triar")
async def triar_mensagem(
    texto: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
):
    # Endpoint principal: recebe texto ou áudio e devolve a ficha de triagem
    if not texto and not audio:
        return JSONResponse(status_code=400, content={"erro": "Envie texto ou arquivo de áudio."})

    origem = "texto"

    if audio:
        # Salva áudio em arquivo temporário e transcreve
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as arquivo_temp:
            arquivo_temp.write(await audio.read())
            caminho_temp = arquivo_temp.name
        texto = transcrever_audio(caminho_temp)
        os.unlink(caminho_temp)
        origem = "audio_transcrito"
        console.print(f"[blue]Transcrição:[/blue] {texto}")

    console.print(f"[green]Processando mensagem:[/green] {texto}")

    intencao = classificar_intencao(texto)
    problema = extrair_problema(texto)
    resultado_rag = buscar_resolucao(problema)

    # Ficha estruturada entregue ao atendente humano
    ficha = {
        "origem": origem,
        "mensagem_original": texto,
        "intencao": intencao,
        "problema_central": problema,
        "resolucao_sugerida": resultado_rag["resolucao"],
        "base_consultada": resultado_rag["base_consultada"],
    }

    console.print("[yellow]Ficha gerada:[/yellow]", ficha)
    return JSONResponse(content=ficha)


@app.get("/health")
async def health():
    return {"status": "ok"}
