from groq import Groq
import os
#https://console.groq.com/keys
api_key = ""
if not api_key:
    print("Missing GROQ_API_KEY. Set it and re-run, e.g.:")
    print('  export GROQ_API_KEY="gsk_..."')
    raise SystemExit(1)

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Explain LLMs in simple terms."}
    ],
    temperature=0.7,
    max_tokens=300,
)

print(response.choices[0].message.content)
