import os
import json
import urllib.request
import urllib.error


class OllamaModel:
    def __init__(self, model=None, base_url=None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.base_url = (base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )).rstrip("/")

    def complete(self, messages, tools=None):
        limit_name = "OLLAMA_TOOL_NUM_PREDICT" if tools else "OLLAMA_FINAL_NUM_PREDICT"
        default_limit = "48" if tools else "512"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": int(os.getenv(limit_name, os.getenv("OLLAMA_NUM_PREDICT", default_limit))),
                "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
            },
        }

        if tools:
            payload["tools"] = tools

        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
            message = result.get("message")
            if not isinstance(message, dict):
                raise RuntimeError("Ollama returned an invalid message")
            return message
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Make sure Ollama is running."
            ) from exc
        except (json.JSONDecodeError, TimeoutError) as exc:
            raise RuntimeError("Ollama returned an invalid or timed-out response") from exc
