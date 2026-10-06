# Docta Insights evaluation

This runner evaluates the running Docta chat endpoint with DeepEval. It builds
a 50-case benchmark from the signed-in user's profile and recent meals, then
asks the live backend the selected 30 or 50 questions. Expected answers are
derived from those records. The runner does not write or modify meal data.

The chat endpoint currently returns the assistant answer but not the agent's
internal tool trace. Therefore, the runner reconstructs representative
retrieval context from the same authenticated profile and meal endpoints. The
contextual metrics are useful end-to-end checks, but they are not a direct
measurement of the exact text passed from the internal tool to the model.

## Install and run

From the repository root in PowerShell:

```powershell
py -3.12 -m venv evaluation\.venv
evaluation\.venv\Scripts\python.exe -m pip install -r evaluation\requirements.txt
evaluation\.venv\Scripts\python.exe evaluation\run_eval.py
```

Start the backend first. The chat model is configured independently with
`LLM_PROVIDER=openai` and `OPENAI_MODEL=gpt-4o-mini` (the backend setting).
By default, the runner calls `http://127.0.0.1:8000`.
It will prompt for the Docta account email and password without saving them. You
can set `DOCTA_API_URL` to evaluate another reachable backend. Copy
`.env.example` to `.env` in this folder to select a judge model.

The chat model and judge are both OpenAI `gpt-4o-mini` by default. The OpenAI
key is read from the repository root `.env` or `backend/.env`. The evaluator
also supports local Ollama as an alternative judge by setting
`DEEPEVAL_JUDGE=ollama` in this folder's `.env`.

Set `EVAL_QUESTION_COUNT=30` for the default run or `EVAL_QUESTION_COUNT=50`
to run the full benchmark. The 30-question run includes 24 personalized
nutrition cases and 6 out-of-scope role checks. The 50-question run includes
44 nutrition cases and the same 6 role checks. The nutrition cases cover user
targets, today's progress, recent meal recall, and seven-day summaries. If there
are no meals in the last seven days, meal-recall questions test that the model
does not invent meal details.

## Metrics

Scores range from 0 to 1. A score below the configured threshold is reported as
FAIL, not as proof that an answer is objectively wrong; LLM judges can vary.

- **Answer relevancy (0.70):** Does the answer address the user's question?
- **Faithfulness (0.70):** Are the answer's factual claims supported by the
  retrieved profile and meal context?
- **Contextual relevancy (0.70):** Is the retrieved context relevant to the
  question?
- **Contextual precision (0.70):** Does the context contain focused, useful
  evidence for the expected answer?
- **Contextual recall (0.70):** Does the context contain the information needed
  for the expected answer?
- **Role adherence (0.80):** Does the chatbot remain a nutrition assistant and
  decline an unrelated programming request?
- **API latency:** Wall-clock time for each chatbot response, reported in
  seconds. This is measured by the runner, not by DeepEval.

All five RAG metrics are run for each nutrition case. Role adherence is run for
six unrelated requests. The benchmark uses authenticated personal records and
does not mutate them.

## Data and cost notes

Both the chatbot and default judge send prompts and relevant profile/meal
context to OpenAI and may incur API charges. Select the Ollama judge if you want
the judging step to stay local; the chatbot still uses OpenAI unless its backend
provider is changed. The script only reads profile and meal endpoints and does
not create meals.
