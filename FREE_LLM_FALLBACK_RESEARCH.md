# Free LLM API Fallback Research (Jul 2026)

Goal: make Hermes "always capable" even if Nous free tier stops. TODO — wire the fallback chain later.

## KEY LESSON
Hermes' full system prompt + tool schemas = >8k tokens per request.
A provider needs HIGH TPM + BIG context or it returns HTTP 413 ("payload too large").
- Groq free = 6–8k TPM → **413s on every full Hermes turn** (confirmed unusable as agent, fine for tiny standalone calls only).
- Non-reasoning models (e.g. Groq llama-3.3-70b) also reject `think`/`reasoning_effort` params with HTTP 400 — only reasoning models accept them.

## Sources cross-referenced
cheahjs/free-llm-api-resources (27k★), freellm.net / awesome-freellm-apis (453 models), nejib1/Free-LLM (45+ providers), OpenRouter live API.

## RECOMMENDED STACK (layered = never down)
| Role | Provider | Free limit | Notes |
|------|----------|-----------|-------|
| PRIMARY | tencent/hy3:free (Nous) | 50 RPM, 500K TPM, 6M tok/HOUR, no expiry | current default, best free deal |
| Fallback 1 | Mistral La Plateforme | **1 BILLION tok/month**, 500K TPM, 1 req/s | near-unlimited; phone verify + data-training opt-in; console.mistral.ai |
| Fallback 2 | Cerebras gpt-oss-120b | 1M tok/day, 14,400 req/day, 60K TPM | reasoning, fastest inference, no card; cloud.cerebras.ai |
| Fallback 3 | Z.AI / Zhipu GLM-5.2 | permanent free, 200K ctx | **NATIVE Hermes support** (GLM_API_KEY) — easiest wiring; open.bigmodel.cn |
| FLOOR | local Ollama (RTX 3050 6GB) | truly unlimited, offline | ~3–8B models; never fails; use CUDA_VISIBLE_DEVICES=-1 if CUDA crash |

## Other confirmed free options
- Google AI Studio: 1,500 req/day (Flash), 1M TPM, 1M context, no 413. Solid daily driver.
- ModelScope (Alibaba): 2,000 req/day permanent, MiniMax-M2.5 / Qwen3.5-397B. api-inference.modelscope.cn/v1
- xAI Grok: **$25/month RENEWING credits** (resets monthly, native XAI_API_KEY).
- NVIDIA NIM: 40 RPM, GLM-5.2 at 1M ctx (phone verify).
- Chutes.ai: community GPU pool, no hard cap (variable speed).
- Kluster.ai: generous free async BATCH quota → good fit for faceless-video script generation (non-interactive).
- HuggingFace: 300 req/hour permanent. Glhf.chat: "unlimited for free models". OVH: 400 RPM auth (EU).
- Trial credits (one-time, stretch weeks): DeepSeek 10M tokens, SambaNova $5 (~30M), DeepInfra $5, Scaleway 1M, Alibaba 1M/model.

## Current state
- Groq custom provider set to openai/gpt-oss-120b (reasoning works on raw call; 413s full Hermes — leave for tiny calls).
- agent.reasoning_effort = medium.

## Next action when we resume
Grab Mistral + Z.AI keys (~5 min), wire Hermes fallback chain (model.fallback), add local Ollama as floor. Z.AI is easiest (native). Kluster.ai worth testing for the video-engine batch script gen.
