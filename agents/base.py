"""Base agent class con integración LLM."""

from __future__ import annotations
import json
import os
from abc import ABC, abstractmethod
from typing import Any

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class BaseAgent(ABC):
    """Clase base para todos los agentes del sistema."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logger.bind(agent=name)
        self.logger.info(f"Agente '{name}' inicializado")

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Ejecuta la tarea principal del agente."""
        ...

    async def llm_call(
        self,
        prompt: str,
        system: str = "",
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        response_format: str = "text",
    ) -> str | dict:
        """Llamada al LLM. Prioridad: Anthropic → Gemini → OpenAI."""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        if anthropic_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=anthropic_key)
                kwargs = {
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}],
                }
                if system:
                    kwargs["system"] = system
                response = client.messages.create(**kwargs)
                text = response.content[0].text
                return self._parse_response(text, response_format)
            except Exception as e:
                if "credit" in str(e).lower() or "balance" in str(e).lower():
                    self.logger.warning("Sin créditos Anthropic → usando Gemini")
                elif "ImportError" not in type(e).__name__:
                    self.logger.warning(f"Error Anthropic: {e} → usando Gemini")

        if gemini_key:
            return await self._gemini_fallback(prompt, system, max_tokens, temperature, response_format)

        return await self._openai_fallback(prompt, system, max_tokens, temperature, response_format)

    def _parse_response(self, text: str, response_format: str) -> str | dict:
        """Parsea la respuesta del LLM según el formato esperado."""
        if response_format == "json":
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        return text

    async def _gemini_fallback(
        self, prompt: str, system: str, max_tokens: int, temperature: float, response_format: str
    ) -> str | dict:
        """Fallback a Google Gemini."""
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system if system else None,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        response = model.generate_content(prompt)
        text = response.text
        return self._parse_response(text, response_format)

    async def _openai_fallback(
        self, prompt: str, system: str, max_tokens: int, temperature: float, response_format: str
    ) -> str | dict:
        """Fallback a OpenAI."""
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = response.choices[0].message.content
        return self._parse_response(text, response_format)

    def log_step(self, step: str, detail: str = ""):
        """Log un paso del agente."""
        msg = f"[{self.name}] {step}"
        if detail:
            msg += f" — {detail}"
        self.logger.info(msg)
