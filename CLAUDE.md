# smart-triage

## Ideia original
Criado por Tayna Azevedo de Almeida como solução para call centers BPO.

## O que este projeto faz
Sistema de triagem inteligente omnichannel para call centers. Recebe mensagens de qualquer canal (chat, email, WhatsApp, áudio transcrito), classifica a intenção do usuário, extrai o problema central, busca a resolução na base de conhecimento da empresa via RAG, e entrega uma ficha padronizada para o atendente humano continuar o atendimento com contexto completo.

## Problema de negócio que resolve
Atendentes de call center perdem tempo tentando entender o que o usuário quer antes de poder ajudar. A IA não substitui o atendente — ela faz a triagem para que o humano chegue na conversa já sabendo o problema, a categoria, e a resolução sugerida. Resultado: atendimento mais rápido, cliente mais bem acolhido.

## Arquitetura
Entrada (texto ou áudio) → Transcrição Whisper se áudio → Classificação de intenção → Extração do problema → Busca RAG na base de conhecimento → Geração da ficha para o atendente.

## Stack
- **Linguagem:** Python 3.14
- **API:** FastAPI + uvicorn
- **Embeddings:** sentence-transformers
- **Banco vetorial:** ChromaDB
- **LLM local:** Ollama (Llama 3.2)
- **Transcrição de áudio:** Whisper
- **Interface de terminal:** Rich

## Padrões de código
- Comentários sempre em português
- A ficha de atendimento deve ser sempre um JSON estruturado
- Todo retorno deve indicar qual base de conhecimento foi consultada

## Comandos
```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o servidor local
uvicorn main:app --reload

# Executar testes
python test_triage.py
```