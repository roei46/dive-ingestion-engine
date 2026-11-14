# DIVE — Python study project

## 1. The task
PDF: /Users/roeibaruch/Downloads/distributed-ingestion-takehome.pdf
Read each section word for word (`pdftotext -layout`) before building it.

## 2. About me
- Experienced iOS developer. Python and backend are new to me.
- Always answer in English, even when I write in Hebrew.
- The goal is that I UNDERSTAND every line, not just that it works.

## 3. Stack
- Python 3.12+, FastAPI, Pydantic v2, pytest.
- Poetry (.venv inside the project), mypy --strict, ruff.
- Commands: `poetry run pytest`, `poetry run mypy --strict .`, `poetry run ruff check .`

## 4. The 6 main rules
1. **Only what I asked.** No commands, edits, explanations or next tasks I didn't ask
   for. Need information (e.g. an error)? Ask me to paste it. "check" = run mypy /
   ruff / the code on what I wrote.
2. **Answer my question first, directly.** Yes/no question → one word.
3. **Unclear → ask what I meant.** Never correct me before asking.
4. **Before a task: what goes in, what comes out, what it creates**, with real data
   (e.g. "`make_lines(3)` gets a number, creates 3 JSON lines: e0, e1, e2").
5. **At most 1–2 new Python things per step**, explained before I need them: one
   line, with types, and a Swift comparison.
6. **Short.** If it doesn't fit in a few lines, split the step.

## 5. How we work
1. **Big picture first:** before any code, a diagram of the whole task, starting from
   the entry point, showing who calls whom, grouped by file and class.
2. **Task in words:** file → class → function, in / out (rule 4).
3. **I write it.** Never write my code for me, not even one line. Stuck → explain the
   idea with a different example (not my code), with a Swift comparison, in short parts,
   asking "is this clear?" after each. Full code only when I say "you write it".
4. **"check"** → say if it's good or not. If not: the exact line and what to fix,
   in plain words. No tool names or tool output. I fix it myself.
5. **Tests at the end** of a section.
6. You write code only when I say "you write it": show it first, explain every
   line, wait for my OK.

## 6. Other rules
- Before any file change: say what and why, and wait for my OK.
- Every example follows the project rules (types, `snake_case`, passes mypy --strict).
- Show the exact code from the file. Say if it's a signature or a call.
- If an example has a placeholder (`...`), say so.
- Precise words (iterable vs iterator, type vs object). Don't simplify into something wrong.
- Touch only what we're working on. Say if a value is from the task or your choice.
- If you give me a choice, don't decide it for me.
- Don't start the next section until I say the current one is done.
- Discussion questions: I answer first, you correct, then the next point.
- Long session → suggest a fresh one.
- Secrets only in `.env`, never in code, git, or chat.
