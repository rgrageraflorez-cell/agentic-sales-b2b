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
        model: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        response_format: str = "text",
    ) -> str | dict:
        """Llamada al LLM. Prioridad: Groq → Anthropic → OpenAI."""
        groq_key = os.getenv("GROQ_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        # 1. Groq (principal, gratis)
        if groq_key:
            try:
                return await self._groq_call(prompt, system, max_tokens, temperature, response_format)
            except Exception as e:
                self.logger.warning(f"Error Groq: {e} → intentando Anthropic")

        # 2. Anthropic (fallback)
        if anthropic_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=anthropic_key)
                kwargs = {
                    "model": model or "claude-sonnet-4-20250514",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}],
                }
                if system:
                    kwargs["system"] = system
                response = client.messages.create(**kwargs)
                return self._parse_response(response.content[0].text, response_format)
            except Exception as e:
                self.logger.warning(f"Error Anthropic: {e} → intentando OpenAI")

        # 3. OpenAI (último recurso)
        return await self._openai_fallback(prompt, system, max_tokens, temperature, response_format)

    async def _groq_call(
        self, prompt: str, system: str, max_tokens: int, temperature: float, response_format: str
    ) -> str | dict:
        """Llamada a Groq (Llama 3.3 70B). Gratis, rápido, sin rate limits agresivos."""
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = response.choices[0].message.content
        return self._parse_response(text, response_format)

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
            text = text.strip()
            # Fallback: extraer JSON con regex si hay texto extra
            if text and not text.startswith(("{", "[")):
                import re
                match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
                if match:
                    text = match.group(1)
            return json.loads(text)
        return text

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
