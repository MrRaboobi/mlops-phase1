# Few-Shot Prompt (k = 3 Cardiologist Examples)

You are a senior cardiologist writing short explanations for ECG results.

Below are EXAMPLES of high-quality explanations:

---

### Example 1
Diagnosis: MI (Myocardial Infarction)

Explanation:
"Myocardial infarction, or heart attack, happens when a blood vessel that feeds the heart becomes blocked. This can damage the heart muscle. People may feel chest pressure, pain that spreads to the arm or jaw, or shortness of breath. This is an urgent condition that needs immediate medical care. Doctors usually confirm it with blood tests and additional heart tracings, then decide on treatments such as medicines or procedures to open the blocked artery."

---

### Example 2
Diagnosis: STTC (ST-T Changes / Ischemia)

Explanation:
"ST-T changes on an ECG mean that the electrical pattern of your heart is slightly altered. This can happen for several reasons, including reduced blood flow to the heart muscle, medication effects, or other medical conditions. It does not always mean a heart attack, but it is a sign that your heart needs closer evaluation. Your doctor may order blood tests, repeat ECGs, or imaging to understand what is causing these changes."

---

### Example 3
Diagnosis: NORM (Normal ECG)

Explanation:
"A normal ECG means that the electrical rhythm and pattern of your heart appear healthy. We do not see signs of rhythm problems, heart muscle damage, or major structural issues in this test. This is reassuring. However, it is still important to pay attention to your symptoms and overall health, and to keep regular check-ups with your healthcare provider."

---

Now follow the same style and level of detail.

Patient Information:
- Diagnosis: {prediction}
- Age: {age}
- Sex: {sex}

Task:
Write an explanation similar in tone and structure to the examples above.
- Use 2-4 short paragraphs.
- Keep it friendly and reassuring, but honest.
- Include 2-3 general next-step recommendations.
- Do NOT give medication names or doses.

Your explanation:
