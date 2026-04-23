# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100.json
- Mode: actual
- Records: 200
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.8 | 0.91 | 0.11 |
| Avg attempts | 1 | 1.3 | 0.3 |
| Avg token estimate | 1863.73 | 2976.59 | 1112.86 |
| Avg latency (ms) | 3364.67 | 5250.13 | 1885.46 |

## Failure modes
```json
{
  "react": {
    "none": 80,
    "wrong_final_answer": 20
  },
  "reflexion": {
    "none": 91,
    "looping": 9
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Reflexion helps when the first attempt stops after the first hop or drifts to a wrong second-hop entity. The tradeoff is higher attempts, token cost, and latency. In a real report, students should explain when the reflection memory was useful, which failure modes remained, and whether evaluator quality limited gains.
