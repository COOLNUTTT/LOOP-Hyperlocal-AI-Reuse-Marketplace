# LOOP Free-Tier Production Deployment & 30–50 Student User-Study Runbook

**Authors & Owners:** Emmanuel George P and Sameer Makani  
**Compliance Scope:** `ROADMAP.md` Phase 18, `PAPER_PLAN.md` §§5–6, `IP_AND_COMPLIANCE.md` §§3, 7.

---

## 1. Free-Tier Cloud Deployment Runbook (`Supabase` + `Render` + `Vercel`)

### Step 1: Hosted Free-Tier Supabase Setup
1. Create a free Supabase project (`loop-demo`) at [supabase.com](https://supabase.com).
2. Open the **Supabase SQL Editor** and execute [`infra/supabase/setup_storage_and_realtime.sql`](../infra/supabase/setup_storage_and_realtime.sql) to enable `postgis`, `vector` (`pgvector`), the `listing-images` Storage bucket + RLS policies, and the `supabase_realtime` publication.
3. Run Alembic migrations (`0001` through `0009`) and seed synthetic demo listings (`data_origin='simulated'`):
   ```bash
   cd apps/api && alembic upgrade head && cd ../..
   python -m scripts.seed
   ```

### Step 2: FastAPI Backend Deployment on Render (`render.yaml`)
1. Connect the private repository to Render using [`render.yaml`](../render.yaml) (`rootDir: apps/api`, free tier).
2. Configure the 5 environment variables (`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`).
3. Verify the deployed healthcheck and ONNX Runtime status:
   - `GET https://<your-api>.onrender.com/api/v1/health` $\rightarrow$ `200 OK`
   - `GET https://<your-api>.onrender.com/api/v1/ai/onnx-status` $\rightarrow$ `all_parity_passed: true`

### Step 3: Next.js 15 PWA Deployment on Vercel (`apps/web/vercel.json`)
1. Import `apps/web` into Vercel using [`apps/web/vercel.json`](../apps/web/vercel.json).
2. Set `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
3. Verify that `/models/quality_mobilenet_v3.onnx` and `/models/scrubber_detector.onnx` are served with `Cache-Control: public, max-age=31536000, immutable` and that the evaluator accounts from [`docs/DEMO_SCRIPT.md`](./DEMO_SCRIPT.md) work on a 360px mobile viewport.

---

## 2. Executing the 30–50 Student Campus User Study (`ROADMAP.md` Phase 18)

### Step 1: Pre-Session Ethics & Anonymisation Checklist
- [ ] Confirm institutional ethics approval or written exemption (`docs/IP_AND_COMPLIANCE.md` §3).
- [ ] Assign each student an anonymous participant code (`LOOP-STU-001` through `LOOP-STU-050`). Store signed consent forms offline and **never** record names, emails, phone numbers, or university roll numbers in the study CSV.

### Step 2: Within-Subjects Session Protocol (Counterbalanced)
1. **Task A (Listing Speed):** Each student creates one listing using **Snap-to-List AI** (`/sell` telemetry timer) and one listing via **Manual Form Entry** (order counterbalanced across odd/even participant codes).
2. **Task B (Explanation Trust):** Each student rates trust (`1–7` Likert) on predictions **with explanations** (Grad-CAM + plain-language SHAP + 80% split-conformal range) vs. **unexplained black-box point output**.
3. **Task C (Discovery, Swap & SUS):** Each student runs a Hinglish search query on `/browse`, reviews a 3-way swap on `/swap`, and completes the 10-item System Usability Scale (`SUS 0–100`).

### Step 3: Ingesting the Anonymised CSV into the Statistical Pipeline
1. Populate your anonymised responses following the exact schema of [`ml/data/templates/user_study_responses_template.csv`](../ml/data/templates/user_study_responses_template.csv):
   ```csv
   participant_anon_id,time_ai_sec,time_manual_sec,trust_explained_1_7,trust_blackbox_1_7,sus_score_0_100,data_origin
   ```
2. Run the PII-guarded statistical analyzer:
   ```bash
   python -m ml.src.eval_user_study_and_ablations --csv ml/data/templates/user_study_responses_template.csv
   ```
   - The script automatically verifies that **zero PII columns** (`name`, `email`, `phone`, `roll_no`, `student_id`) exist, and outputs paired $t$-statistics, two-sided $p$-values, 95% confidence intervals, Cohen's $d$, Wilcoxon signed-rank $W$ & $z$, and SUS mean/SD/median/IQR.
