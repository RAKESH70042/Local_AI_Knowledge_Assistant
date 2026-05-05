import ollama
stream = ollama.chat(
    model='qwen2.5:0.5b',
    messages=[{'role': 'user', 'content': 'say hello'}],
    stream=True
)
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
print()