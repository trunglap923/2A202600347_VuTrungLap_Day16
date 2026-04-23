import time
import os
from openai import OpenAI
from .schemas import QAExample, JudgeResult, ReflectionEntry
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> tuple[str, int, int]:
    start_time = time.time()
    
    # Format context
    context_str = "\n".join([f"Title: {c.title}\nText: {c.text}" for c in example.context])
    
    prompt = f"Question: {example.question}\n\nContext:\n{context_str}"
    
    if reflection_memory and agent_type == "reflexion":
        reflections_str = "\n".join([f"- {r}" for r in reflection_memory])
        prompt += f"\n\nPrevious Reflections (Do not repeat these mistakes!):\n{reflections_str}"
        
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": ACTOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    tokens = response.usage.total_tokens if response.usage else 0
    answer = response.choices[0].message.content or ""
    
    return answer, tokens, latency_ms

def evaluator(example: QAExample, answer: str) -> tuple[JudgeResult, int, int]:
    start_time = time.time()
    prompt = f"Question: {example.question}\nGold Answer: {example.gold_answer}\nPredicted Answer: {answer}"
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EVALUATOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        response_format=JudgeResult,
        temperature=0.0
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    tokens = response.usage.total_tokens if response.usage else 0
    result = response.choices[0].message.parsed
    
    return result, tokens, latency_ms

def reflector(example: QAExample, attempt_id: int, answer: str, judge: JudgeResult) -> tuple[ReflectionEntry, int, int]:
    start_time = time.time()
    context_str = "\n".join([f"Title: {c.title}\nText: {c.text}" for c in example.context])
    
    prompt = f"""
Question: {example.question}
Context: {context_str}
Gold Answer: {example.gold_answer}
Agent's Predicted Answer: {answer}
Evaluator's Feedback: {judge.reason}
"""
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": REFLECTOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        response_format=ReflectionEntry,
        temperature=0.0
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    tokens = response.usage.total_tokens if response.usage else 0
    result = response.choices[0].message.parsed
    result.attempt_id = attempt_id
    result.failure_reason = judge.reason
    
    return result, tokens, latency_ms
