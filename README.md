# RAG Document Q&A

Take today's [RAG Pattern lesson](https://github.com/CP-Evenings-and-Weekends/curriculum/blob/main/Module_06_AI_LLMs/week17/day2/README.md) and build it end-to-end as your own project: ingest documents, chunk + embed them, retrieve the most relevant chunks for a question, and have the LLM answer using just that context.

The repo ships the same `docker-compose.yml` and `requirements.txt` you used for yesterday's pgvector exercise, so the infrastructure isn't the work — the work is the RAG pattern itself.

## Setup

```bash
cp .env.example .env
# Put your AI_API_KEY in .env (or use Ollama — see lesson)
docker compose up -d
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Then scaffold a fresh Django project + `rag` app (don't paste yesterday's project — start clean to lock the pattern in):

```bash
django-admin startproject rag_project .
python manage.py startapp rag
```

Wire `"rag"` into `INSTALLED_APPS`, configure `DATABASES` against the pgvector container, and you're ready to build.

## Assignment 1 — Document ingestion management command

A Django management command that turns a text file into searchable chunks.

### Required behavior

```bash
python manage.py ingest_document path/to/file.txt --title "Company Handbook"
```

The command should:

1. Read the file from disk
2. Create a `Document` row (full content stored)
3. Chunk the content using **paragraph-based** chunking with `max_chunk_size=1000` chars
4. **Batch-embed** the chunks (the lesson's `generate_embeddings_batch` — one API call per batch of 20, not one per chunk)
5. Bulk-create `DocumentChunk` rows with `chunk_text`, `chunk_index`, `embedding`, and a FK to the Document

### Models you need

- `Document` — `title`, `content`, `created_at`
- `DocumentChunk` — FK to Document (`related_name="chunks"`), `chunk_text`, `chunk_index`, `embedding = VectorField(dimensions=1536)`

### Verify

Drop a real text file (a long blog post, a README, a public-domain book chapter) and run the command.  Inspect via Django shell:

```python
Document.objects.count()           # 1
DocumentChunk.objects.count()      # many
DocumentChunk.objects.first().embedding[:5]  # first 5 floats of the vector
```

## Assignment 2 — Q&A endpoint

A DRF endpoint that takes a question, retrieves the top 3 most relevant chunks, and asks the LLM to answer using only those chunks.

### Required endpoint

`POST /api/ask/` accepting `{"question": "..."}`.  Returns:

```json
{
  "answer": "<LLM-generated answer>",
  "sources": [
    {
      "document": "Company Handbook",
      "text_preview": "...",
      "relevance_score": 0.89
    }
  ]
}
```

### Required behavior

1. Embed the question
2. Use `CosineDistance("embedding", query_embedding)` to find the top **3** most relevant chunks across **all** documents
3. Build the LLM prompt:
    - System: instructs the LLM to **only** use the provided context, **say so** if the context is insufficient, and **never** fabricate
    - User: the question itself
4. Call the LLM with `temperature=0.3` (we want grounded, not creative)
5. Return the answer AND the source chunks (title + a ~200-char preview + a relevance score derived from distance)

### Verify

```bash
curl -X POST http://localhost:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the document say about onboarding?"}'
```

Try at least three kinds of questions:

- **A question the document clearly covers** — should answer from sources
- **A question the document doesn't cover at all** — the LLM should say so, not make something up
- **A question where the answer requires synthesizing two chunks** — does the LLM blend them sensibly?

## Things to think about
- The lesson's example uses a 0.3 temperature on the generation step.  What happens if you bump it to 0.9?  Why is lower better for RAG?
- If the top-3 chunks are all from the same document, is that good or bad?  When would you want diverse documents in your top-k?
- The lesson explicitly tells the LLM "do not make up information that is not in the context."  Try **removing** that instruction and asking a question the docs don't cover.  Does the LLM hallucinate?
- Why do we batch embeddings (one API call per 20 chunks) instead of one call per chunk?  How much faster is it in practice?  How much cheaper?

## Stretch
- **Re-ranking**: wire the lesson's `rerank_chunks` function into your retrieval pipeline — fetch the top-10 from pgvector, run them through the LLM reranker, and only feed the top-3 of those reranked chunks into the final answer prompt. Does the answer quality change on your harder questions?
- **Metadata filter**: extend `POST /api/ask/` to accept an optional `document_id` so the user can scope the search to a single document.
- **Source citations inline**: change the prompt to ask the LLM to cite sources in the format `[Source: <title>]` after each claim it makes.
- **Streaming**: stream the LLM's answer back to the client using SSE so the answer renders word-by-word in a frontend.
- **Two chunking strategies**: implement both fixed-size *and* paragraph-based chunking, run the same query against each, and write up which strategy worked better and why.

> Stuck? Have a code error? Use the ["4 Before Me"](https://docs.google.com/document/d/1nseOs5oabYBKNHfwJZNAR7GlU0zkZxNagsw63AD7XV0/edit) debugging checklist to help you solve it!
