# Model Card: Multilingual Semantic Search & Query Parser (`semantic_search`)

- **Version:** `v1.0.0`
- **License:** Permissive (Apache-2.0 / MIT compatible)
- **Data Origin:** Evaluated on 50-query English + Hinglish benchmark (`data_origin='simulated'`)

## 1. Intended Use & Architecture
- **Task:** Retrieve hyperlocal campus listings across English and Romanized Hinglish queries (e.g., `"sasta study table under 3000 near Wakad"`), combining rule-based price/location extraction with 384-d text embeddings and 512-d image embeddings in PostgreSQL `pgvector` (HNSW).
- **Baseline:** PostgreSQL Full-Text Search (`mode=fts`).

## 2. Evaluation Metrics (50-Query Benchmark: 25 English + 25 Hinglish)
| Slice | System | Recall@5 | NDCG@10 | MRR | p95 Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **English (25 queries)** | FTS Baseline | 0.9600 | 0.9480 | 0.9400 | < 5 ms |
| **English (25 queries)** | Semantic + Parser | **1.0000** | **0.9926** | **0.9900** | < 8 ms |
| **Hinglish (25 queries)** | FTS Baseline | 0.8000 | 0.8400 | 0.8200 | < 5 ms |
| **Hinglish (25 queries)** | Semantic + Parser | **1.0000** | **0.9852** | **0.9800** | < 8 ms |

## 3. Limitations
- Unseen regional slang outside the Hinglish lexicon falls back to character-trigram and vector cosine similarity.
