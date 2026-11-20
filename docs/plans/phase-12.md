# Phase 12: Semantic Multilingual Search, Image Search & Saved Searches Implementation Plan

> **Goal:** Implement semantic multilingual search (English + Hinglish), image-based search, "similar items" recommendations, and saved searches with alert matching per `ROADMAP.md` Phase 12 and `DATA_MODEL_AND_API.md`:
> 1. Database migration `0005_embeddings_and_saved_searches` adding `text_embedding` (384-d) and `image_embedding` (512-d) columns with HNSW indexing support on `listings`, plus `saved_searches` table with RLS.
> 2. Multilingual embedding worker & natural-language query parser (`ml/src/semantic_search.py`) supporting 384-d text embeddings, 512-d image embeddings, Hinglish-to-English synonym/transliteration mapping, and structured constraint parsing (price ceiling e.g. `"under 3000"`, place e.g. `"near Wakad"`).
> 3. Search API enhancements: `mode=semantic|fts` on `GET /listings`, `POST /listings/search-by-image`, `GET /listings/{id}/similar`, and `/saved-searches` CRUD + alert matching.
> 4. 50-query evaluation harness (English vs Hinglish) measuring `Recall@5`, `Recall@10`, `NDCG@10`, `MRR`, and query latency (`ml/reports/semantic_search/report.md`).
> 5. Frontend integration: `/browse` search bar with semantic/image search & save-search button, plus "Similar Items" on `/listings/[id]`.
> 6. Automated acceptance tests verifying query parsing, semantic vs FTS ranking, image similarity, and saved search matching.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p12-task-1 | Migration `0005_embeddings_and_saved_searches` & `SavedSearch` model | completed | 384-d text & 512-d image vectors + `saved_searches` RLS |
| p12-task-2 | Multilingual embedding worker & query parser (`ml/src/semantic_search.py`) | completed | English + Hinglish, price ceiling & place extraction |
| p12-task-3 | Search API endpoints (`mode=fts|semantic`, image search, similar, saved) | completed | `GET /listings`, `/search-by-image`, `/similar`, `/saved-searches` |
| p12-task-4 | 50-query evaluation (English vs Hinglish) & benchmark report | completed | Recall@k, NDCG@10, MRR, latency vs FTS baseline |
| p12-task-5 | Frontend `/browse` & `/listings/[id]` similar items + saved search UI | completed | API-ready endpoints for browse & detail pages |
| p12-task-6 | Acceptance tests & Phase 12 completion report | completed | Verify query parser, ranking, image search & saved alerts |
