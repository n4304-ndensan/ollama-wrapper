# ollama-wrapper

Ollama を Python から叩くための軽量ラッパーです。

前提
- Ollama が起動していること

起動
  ollama serve

モデル取得（例）
  ollama pull gpt-oss:20b


インストール（uv推奨）
1) 依存に追加
  uv add "git+https://github.com/n4304-ndensan/ollama-wrapper"

2) 同期
  uv sync


AsyncOllamaTextClient の概要
- asyncio で非同期に chat() を呼べます
- requests/min, tokens/min の簡易レート制限に対応
- 使用量（token 等）は取得できれば実測、無理なら推定してログ出力できます


使い方（最小）
```py
  import asyncio
  import logging
  from ollama_wrapper import AsyncOllamaTextClient, ClientConfig

  logging.basicConfig(level=logging.INFO)

  async def main():
      client = AsyncOllamaTextClient(
          ClientConfig(
              model="gpt-oss:20b",
              requests_per_minute=60,
              tokens_per_minute=40000,
              log_usage=True,
          )
      )
      try:
          text = await client.chat("こんにちは")
          print(text)
      finally:
          await client.close()

  asyncio.run(main)
```

JSONが欲しい場合（推奨：system_promptを固定）
```py
  import asyncio
  from ollama_wrapper import AsyncOllamaTextClient, ClientConfig
  from ollama_wrapper.prompts import JSON_ONLY_SYSTEM_PROMPT

  async def main():
      client = AsyncOllamaTextClient(ClientConfig(model="gpt-oss:20b"))
      try:
          text = await client.chat(
              message="次をJSON化して: A=1, B=2",
              system_prompt=JSON_ONLY_SYSTEM_PROMPT,
              expect_json=True,
          )
          print(text)
      finally:
          await client.close()

  asyncio.run(main)
```


手順まとめ
1. ollama serve でサーバ起動
2. ollama pull <model> でモデル取得
3. uv add "git+https://github.com/n4304-ndensan/ollama-wrapper"
4. uv sync
5. 上記サンプルを uv run python <script>.py で実行
