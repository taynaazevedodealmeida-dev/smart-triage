# smart-triage

Sistema de triagem inteligente omnichannel para call centers BPO.

A IA não substitui o atendente — ela faz a triagem para que o humano chegue na conversa já sabendo o problema, a categoria e a resolução sugerida.

---

## Como funciona

```
Entrada (texto ou áudio)
        ↓
Transcrição Whisper (se áudio)
        ↓
Classificação de intenção (Llama 3.2)
        ↓
Extração do problema central (Llama 3.2)
        ↓
Busca RAG na base de conhecimento (ChromaDB)
        ↓
Ficha JSON entregue ao atendente
```

---

## Stack

| Componente | Tecnologia |
|---|---|
| API | FastAPI + uvicorn |
| LLM local | Ollama (Llama 3.2) |
| Embeddings | sentence-transformers |
| Banco vetorial | ChromaDB |
| Transcrição de áudio | Whisper |
| Interface de terminal | Rich |

---

## Instalação

**Pré-requisitos:** Python 3.11+, [Ollama](https://ollama.com) instalado e rodando com o modelo `llama3.2`.

```bash
# Clonar o repositório
git clone https://github.com/taynaazevedodealmeida-dev/smart-triage.git
cd smart-triage

# Instalar dependências
pip install -r requirements.txt

# Baixar o modelo no Ollama (se ainda não tiver)
ollama pull llama3.2
```

---

## Uso

```bash
# Iniciar o servidor
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/triar` | Recebe texto ou áudio e retorna a ficha de triagem |
| GET | `/health` | Verifica se a API está no ar |

### Exemplo de requisição (texto)

```bash
curl -X POST http://localhost:8000/triar \
  -F "texto=Minha internet caiu há três dias e ninguém me atendeu ainda"
```

### Exemplo de resposta

```json
{
  "origem": "texto",
  "mensagem_original": "Minha internet caiu há três dias e ninguém me atendeu ainda",
  "intencao": "RECLAMACAO",
  "problema_central": "Internet sem funcionamento há três dias sem atendimento",
  "resolucao_sugerida": "Verificar status da linha e agendar visita técnica em até 24h",
  "base_consultada": "base_conhecimento"
}
```

### Exemplo de requisição (áudio)

```bash
curl -X POST http://localhost:8000/triar \
  -F "audio=@gravacao.wav"
```

---

## Testes

```bash
python test_triage.py
```

---

## Autora

Tayna Azevedo de Almeida
