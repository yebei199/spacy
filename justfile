# 当前只能用于本地开发或者windows环境下调试

set shell := ["fish", "-c"]
set dotenv-load := true
set export := true

uv_sync:
    uv sync --all-extras

uv_sync_force:
    rm uv.lock
    uv sync --all-extras

spacy_download:
    uv pip install spacy
    uv run python -c "import spacy; "
