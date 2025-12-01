#Prompt Engineering Evaluation Report

## Strategies Evaluated

- **baseline_zero_shot** – simple direct instruction
- **few_shot_k3** – example-driven with 3 cardiologist summaries
- **advanced_cot** – chain-of-thought + risk-factor reasoning

## Quantitative & Qualitative Metrics (averages)

| Strategy | ROUGE-L | BLEU | Factuality (1-5) | Helpfulness (1-5) |
|----------|---------|------|-------------------|-------------------|
| baseline_zero_shot | 0.067 | 0.000 | 3.00 | 3.20 |
| few_shot_k3 | 0.137 | 0.000 | 5.00 | 4.00 |
| advanced_cot | 0.095 | 0.000 | 3.00 | 2.80 |

## Summary & Winner

- Highest **Helpfulness**: **few_shot_k3**
- Highest **Factuality**: **few_shot_k3**

Overall, the advanced chain-of-thought strategy often produces more detailed and tailored explanations, but the few-shot strategy can be more concise and style-consistent. The zero-shot baseline is simplest but tends to be less robust for edge cases.
