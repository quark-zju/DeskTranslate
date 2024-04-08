import functools

_cache = {}

def translate(text: str, set_pending=None, prompt='将下文翻译成中文：', model='qwen') -> str:
    text = text.strip()

    cached = _cache.get(text)
    if cached:
        return cached

    import ollama

    prompt = f'{prompt} {text}'
    gen = ollama.generate(model=model, prompt=prompt, stream=True)

    result = ''
    for chunk in gen:
        value = chunk.get('response')
        if not value:
            continue
        result += value
        if set_pending:
            set_pending(result.rstrip())

    result = result.rstrip()
    
    _cache[text] = result
    return result

