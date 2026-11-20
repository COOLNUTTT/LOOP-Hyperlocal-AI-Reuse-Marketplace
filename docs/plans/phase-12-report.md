# Phase 12: Semantic Multilingual Search, Image Search & Saved Searches Completion Report

> **Date:** October 2026  
> **Status:** Completed  
> **Scope:** Multilingual Semantic Search (English + Hinglish), 512-d Image Search, Similar Items & Saved Searches

---

## 1. Executive Summary

Phase 12 delivers multilingual semantic search, image-based discovery, and saved search alerts per `ROADMAP.md` Phase 12:
1. **Database & Migration (`0005_embeddings_and_saved_searches`):**
   - Added 384-d `text_embedding` and 512-d `image_embedding` vector columns with HNSW cosine indexes on `listings`.
   - Created `saved_searches` table (`apps/api/app/models/saved_search.py`) with PostgreSQL Row Level Security (RLS).
2. **Multilingual Embedding Worker & Query Parser (`ml/src/semantic_search.py`):**
   - Extracts structured constraints from natural-language English and Hinglish queries (e.g., `"study table under 3000 near Wakad"` and `"padhai ki mez 3000 ke andar Wakad ke paas"`).
   - Generates 384-d normalized text embeddings and 512-d image embeddings.
3. **Search APIs (`apps/api/app/routers/listings.py`, `apps/api/app/routers/saved_searches.py`):**
   - `GET /listings?mode=semantic|fts` with automatic price/place constraint extraction.
   - `POST /listings/search-by-image` using 512-d image similarity.
   - `GET /listings/{id}/similar` for detail-page recommendations.
   - `POST/GET/DELETE /saved-searches` with `SearchService.matches_saved_search`.
4. **50-Query Evaluation (`ml/reports/semantic_search/report.md`):**
   - **Hinglish (25 queries):** Semantic achieved `Recall@5 = 1.0000`, `NDCG@10 = 0.9852`, `MRR = 0.9800` vs FTS baseline `Recall@5 = 0.8800`, `NDCG@10 = 0.8400`, `MRR = 0.8267`.
   - **English (25 queries):** Semantic achieved `Recall@5 = 1.0000`, `NDCG@10 = 0.9557`, `MRR = 0.9400`.
5. **Acceptance Testing:**
   - `apps/api/tests/test_semantic_search_acceptance.py`: All 4 acceptance tests passed.
