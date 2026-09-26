<!-- STATUS_4.md: owned by instance 4 (repo hygiene, deploy, README, one-pager). The five-line summary printed after each
     brief step, appended in the order the steps finished, newest at the bottom; later entries supersede earlier ones. -->
# Instance 4 (repo, deploy, docs): step status

## Step 1: repo hygiene (01:36)
1. Repo on `main`; the first commit `5a4e4d7` holds only `.gitignore`, `.gitattributes`, `.env.example`.
2. `.gitignore`: the brief's list plus the SQLite variants (thread state holds case data), and `!.env.example`, because `.env.*` would hide the template.
3. `.gitattributes` forces LF; `git ls-files --eol` shows `i/lf w/lf` on every tracked file.
4. `.env.example`: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `EVAL_JUDGE`, `VITE_API_BASE` (front end, commented); names only; no tracing keys, on purpose.
5. `0c81909` adds `CLAUDE.md` and `spec.md`; the key-prefix tripwire was clean on both staged diffs.

## Step 2: backend Dockerfile (01:40)
1. Base `python:3.13.15-slim-trixie` pinned by digest; non-root `app` (uid 10001); uvicorn on 8080; `/health` as the HEALTHCHECK, called with Python (no curl in slim).
2. Phase 1 serves `deploy/hello_app.py` because `backend/app.py` did not exist; step 7 swaps in `requirements.txt`, `backend/`, `data/` and `backend.app:app`.
3. `.dockerignore` keeps `.env*`, `frontend/`, `node_modules`, `chroma/`, databases, logs, `eval/`, `docs/` out; `**/` patterns, because a bare `*.log` matches the root only.
4. Proof: build exit 0 (198 MB); container `healthy`; `/health` returned `{"ok":true,"service":"priorauth-hello",...}`; runs as `uid=10001(app)`.
5. Commit `2c1b989`. Caveat: unpinned transitive deps gave pydantic 2.13.5 in the image (2.12.5 on the box), so phase 2 installs from the pinned `requirements.txt`.

## Step 4: README (01:52)
1. `README.md`: what it is (spec items 1 to 9, condensed) and one paragraph on how it is built.
2. Run locally: `.env` from `.env.example`, then five commands (pip install, npm ci, ingest, uvicorn on 8000, vite on 5173); `VITE_API_BASE` unset means the mock client.
3. Eval: `python eval/run_eval.py`; the code-graded half gates, the control must fail, `failed_to_score` must be 0, the judge is capped at $2, and it says what it does not measure.
4. Deployed table, environment variable names table, and a before-every-push section that never spells out the key prefixes (the tripwire would match its own docs).
5. With-a-week: 7 lines (the narration card list plus the SQLite-on-an-ephemeral-disk limit); a slot is open for lines from instances 1 and 3.

## Step 5: one-pager and PDF (01:52)
1. `docs/one_pager.md`: exactly the four headings, made from the Spec section of `CLAUDE.md`, not from the code.
2. The read-back rewrote 6 sentences: "prior authorization" and the three procedures explained, "never decides whether", "practice mailbox", "activity records".
3. Banned words and product names: 0 hits in reader-visible text; no diagram, no image.
4. `docs/one_pager.pdf`: 1 page, 39 KB, printed by `docs/build_pdf.py` (standard library plus headless Edge; no pandoc on the box, no new dependency).
5. Commit `e6a24bc`, held from the push so App Platform's first build would not be superseded.

## Step 3: hello-world deploy (02:02)
1. GitHub: https://github.com/TheZigula/priorauth-assistant-dryrun1, public; the first push went only after tripwire 0 hits and detect-secrets `{}`.
2. Vercel: project `priorauth-assistant-dryrun1`, linked by explicit name (a shakedown project called `frontend` exists); https://priorauth-assistant-dryrun1.vercel.app answers 200, mock mode.
3. App Platform: https://plankton-app-kkdyy.ondigitalocean.app/health answers `"service":"priorauth-hello"`, this repo's placeholder, proved by service name; the payload has no commit field.
4. Hazards logged: the leftover shakedown app answered 200 as "hello-backend" (caught by the service name); `vercel link` wrote a token file (deleted unread); `doctl` returns 401.
5. Cannot yet: serve the real backend; no keys are set on either host (the placeholder needs none).

## Step 6: pre-push controls (standing; latest run 02:02)
1. Tripwire on every staged diff before each commit (9 in history), and across all unpushed commits before a push: 0 hits every time.
2. detect-secrets scans every file git could push (your call at 01:45, after `--all-files` took 75 s and flagged 112 `node_modules` strings); `{}` for the first push.
3. Latest run: 1 entry, `backend/ingest.py:129` "Secret Keyword": the flagged text is the name of the OpenAI key's environment variable, not a key. A false positive, and the gate still blocks.
4. Push of the held commits is BLOCKED until instance 3 appends `# pragma: allowlist secret` to that line, or you say push anyway.
5. The scanner catches what it knows; the tripwire catches what I know I hold.
