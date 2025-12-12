# 当前只能用于本地开发或者windows环境下调试

set shell := ["fish", "-c"]
set dotenv-load := true
set export := true

uv_sync:
    rm uv.lock
    uv sync --all-extras
