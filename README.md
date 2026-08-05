# Chat with Docs

Upload a PDF, get a chat UI grounded in that document via RAG. Built as a coding assessment: keep the path simple, make the retrieval choices explicit, leave a clear trail for what would change in production.

---

## a. Quick setup

**Prereqs**

- Python 3.11+ (developed against 3.12)
- An Ollama server reachable from this machine, with the model you set in `.env` pulled (`ollama pull dolphin-mistral` or whatever you configure)
- ~1–2 GB free RAM for the embedding model on CPU

**Steps**

```bash
git clone <this-repo>
cd chat_with_docs

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env        # or create .env from the block below
# edit OLLAMA_URL / OLLAMA_MODEL if needed

flask --app app run
# or: python app.py
```

Open `http://127.0.0.1:5000`, upload a PDF, chat.

**`.env`**

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=dolphin-mistral:latest
HUGGING_FACE_MODEL_NAME=BAAI/bge-small-en
HUGGING_FACE_MODEL_KWARGS=cpu
CHROMA_PATH=./tmp/chroma
UPLOAD_FOLDER=static/tmp/
RELEVANCE_THRESHOLD=0.7
```

---

## b. Architecture overview

```
Browser (templates + static JS)
        |  POST multipart PDF
        v
   Flask app.py
        |-- ingest_pdf(file, doc_id)     chatpdf/ingest.py
        |       PyPDFLoader → chunk → HuggingFaceEmbeddings → Chroma(persist/doc_id)
        |
        |-- POST /api/chat { prompt, doc_id }
                answer_query()           chatpdf/query.py
                    Chroma similarity search (k=3, score gate)
                    → ChatPromptTemplate + ChatOllama
```

**Layout**

| Piece | Role |
|-------|------|
| `app.py` | HTTP: upload, chat page, JSON chat API |
| `chatpdf/config.py` | Env + per-doc Chroma path helper |
| `chatpdf/embeddings.py` | Process-wide embedding singleton |
| `chatpdf/ingest.py` | PDF → chunks → vector index |
| `chatpdf/query.py` | Retrieve + prompt + Ollama |
| `templates/` / `static/` | Upload + chat UI (localStorage holds `doc_id` + rendered chat) |

Each upload gets a `doc_id` (`timestamp_safeName`). Its Chroma store lives under `CHROMA_PATH/<doc_id>/` so documents don’t bleed into each other. Chat requests must send that `doc_id`.

---

## c. Productionizing & scaling (AWS / GCP / Azure / Cloudflare)

This repo is a single-process demo. To put it on a hyperscaler I’d treat it as three concerns: **API**, **async ingest**, **retrieval + LLM**.

**Must-fix before any public deploy**

- Upload size/type limits (`MAX_CONTENT_LENGTH`, magic-byte checks), virus scan if policy requires it
- Stop storing PDFs under `static/` (they’re web-reachable today)
- Auth (signed URLs / sessions / API keys); no open CORS
- Escape user text in the UI (today outbound messages use `innerHTML`)
- Relative `/api/chat` URL instead of hardcoded `127.0.0.1:5000`
- Secrets in a vault / SSM / Secret Manager, not a committed mental model of `.env`

**Shape that scales**

1. **API tier** — containerized Flask (or FastAPI) behind ALB / Cloud Run / App Service / Cloudflare Workers + a real ASGI/WSGI server (gunicorn/uvicorn). Stateless; scale horizontally.
2. **Object storage** — S3 / GCS / Azure Blob for PDFs; DB row maps `doc_id` → object key + index status.
3. **Ingest workers** — upload returns `202` + job id; a queue (SQS / Pub/Sub / Service Bus) runs chunk+embed. Don’t block the HTTP thread like we do now.
4. **Vector DB** — managed (OpenSearch k-NN, Vertex Matching Engine, Azure AI Search, Pinecone, or Cloudflare Vectorize). Drop local Chroma directories.
5. **Embeddings / LLM** — hosted APIs or private endpoints (Bedrock, Vertex, Azure OpenAI, or self-hosted GPU pool). Keep the same retrieve→prompt interface so the app doesn’t care which vendor.
6. **Observability** — request ids, ingest latency, retrieval score histograms, token usage, groundedness / “no context” rates; OpenTelemetry into CloudWatch / Cloud Trace / App Insights / Cloudflare Analytics.

**Cost / ops notes**

- CPU embeddings are fine for assessment load; in prod I’d batch embeds on workers and cache the model in the worker image.
- LLM is the expensive/slow hop — stream tokens, set timeouts, circuit-break Ollama/API failures.
- Multi-tenant: namespace by `tenant_id` + `doc_id` in the vector store; never share a flat folder like this demo.

---

## d. RAG / LLM approach & decisions

### LLM

| Option | Why considered | Why not / why yes |
|--------|----------------|-------------------|
| Hosted GPT / Claude | Quality, tools, streaming | Needs API keys, cost; assessment asked for something runnable locally with Ollama |
| **Ollama (`dolphin-mistral`)** | Local/remote URL, no vendor lock in code, matches the starter brief | Final choice. Quality depends on the box you point `OLLAMA_URL` at |
| Smaller local models | Faster CPU | Worse instruction following for “answer only from context” |

Chat goes through `langchain-ollama` `ChatOllama`. One call per question — no agent loop.

### Embeddings

| Option | Notes |
|--------|--------|
| OpenAI `text-embedding-3-*` | Strong, paid, network |
| **`BAAI/bge-small-en` via `HuggingFaceEmbeddings`** | Small enough for CPU, solid for English PDF Q&A, offline after first download |
| Larger BGE / E5 | Better recall, heavier cold start |

Normalized embeddings (`encode_kwargs.normalize_embeddings=True`) so cosine/relevance scores behave more sanely with Chroma.

### Vector store

| Option | Notes |
|--------|--------|
| FAISS in-memory | Fast, dies with process |
| **Chroma persisted per `doc_id`** | Zero ops for a demo, disk persistence, easy wipe/rebuild on re-ingest |
| Postgres/pgvector | Better for “real” multi-user later |

Early versions of this idea shared one Chroma path and wiped it on every upload. That’s fine for a single-session toy; wrong if two uploads or a refresh should still work. Per-doc directories fixed that.

### Orchestration

**LangChain** (community loaders, text splitters, Chroma + HF + Ollama integrations) rather than a hand-rolled HTTP client stack. I didn’t pull in LangGraph / agents — overkill for “retrieve k chunks, stuff prompt, generate.”

Chunking: `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)`. Overlap helps when a sentence straddles a boundary; 1000 is a boring but workable default for dense prose PDFs.

### Prompt & context

Strict “answer from context only” template. If top relevance score &lt; `RELEVANCE_THRESHOLD` (default `0.7`), context becomes `"no context found"` so the model is nudged to refuse rather than invent. Retrieval `k=3` — enough signal for short questions without flooding a small local model’s window.

**Not in this build (on purpose):** multi-turn rewrite, HyDE, rerankers, citation UI. Follow-ups like “what about him?” will retrieve poorly without conversational query rewriting; I left that as a known gap rather than half-ship it.

### Guardrails / quality / observability

- **Guardrails (light):** relevance gate; PDF extension check; `secure_filename`; API validates `prompt` + `doc_id`.
- **Missing:** jailbreak/prompt-injection filters, PII redaction, max upload size, output schema checks, source citations in the response JSON.
- **Quality:** manual PDF Q&A while building; no golden-set eval harness yet.
- **Observability:** Flask `logger.exception` on ingest/chat failures. No metrics/tracing.

---

## e. Key technical decisions

1. **Per-document indexes** — isolation &lt; shared collection with metadata filters for a take-home. Filters are the production move; folders were faster to reason about and debug.
2. **Singleton embeddings + LLM** — loading `sentence-transformers` every request was painfully slow on CPU. Lazy globals in `embeddings.py` / `query.py` are blunt but effective for one process.
3. **Sync ingest in the upload request** — honest about latency (“this may take a while”). Wrong for scale; right for “one process, no Redis” assessment timebox.
4. **`doc_id` in localStorage** — ties the chat page to the index without a session DB. Fragile across browsers/devices; fine for a demo.
5. **Threaded Flask** — one stuck Ollama call shouldn’t freeze every other tab when running `python app.py`.
6. **Minimum-version `requirements.txt`** — assessment machines differ; pins-to-the-patch would fight that. Tradeoff: less reproducible builds.

---

## f. Engineering standards followed (and skipped)

**Followed**

- Split domain logic out of routes (`ingest` / `query` / `config`)
- Env-driven config with defaults where safe
- Explicit API errors (400 vs 500), no stack traces to the client
- `.gitignore` for `.venv`, `.env`, `tmp/`, upload debris
- Type hints on the hot path functions

**Skipped / light**

- Automated tests (unit for chunking/threshold logic, API smoke tests)
- Upload size limits and non-`static` storage
- XSS-safe rendering for user messages
- CI, lint config, pre-commit, typed frontend
- Structured logging / request IDs
- Dead weight cleanup discipline under time pressure (`static/chat.js` is empty leftover)

I wouldn’t pretend those skips are “fine forever” — they’re timebox choices.

---

## g. How AI tools showed up in development

Used Cursor as a pair programmer: scaffolding Flask routes, LangChain import churn (`langchain_community` → `langchain_huggingface` / `langchain_chroma`), and “why is this Chroma path wrong” debugging. I treated suggestions as drafts — especially around RAG prompts and threshold defaults — and verified behavior against real PDFs and a live Ollama endpoint.

What I didn’t do: paste an entire generated app and ship it. The interesting bits (per-doc stores, score gate, what *not* to build) came from running the thing and deciding what failed in practice.

---

## h. What I’d do with more time

1. Conversational retrieval (rewrite follow-ups using history) + send history from the client
2. Stream tokens to the UI; show retrieved chunk citations
3. Background ingest + progress polling
4. `MAX_CONTENT_LENGTH`, private upload storage, relative API URLs, escape user HTML
5. A tiny eval set (10 questions per sample PDF) and a script that scores “answered / refused / hallucinated”
6. Swap Chroma for a managed vector DB and run the API under gunicorn in Docker
7. Basic pytest coverage for ingest failure modes and the relevance gate

---

## License / UI credit

MIT. Chat UI styling inspired by [Emma Delaney’s Medium write-up](https://emma-delaney.medium.com/how-to-create-your-own-chatgpt-in-html-css-and-javascript-78e32b70b4be).
