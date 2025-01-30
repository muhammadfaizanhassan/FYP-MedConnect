from llama_cpp import Llama

llama = Llama(
    model_path="C:\\Users\\pc\\OneDrive\\Desktop\\models\\llamaModel.gguf",
    n_gpu_layers=50,
    n_ctx=2048,
    n_batch=256,
    n_threads=8,
    use_mmap=True,
    use_mlock=True,
    verbose=False
)

def Asklama(prompt, tokens):
    for output in llama(
        prompt,
        max_tokens=tokens,
        temperature=0.7,
        top_p=0.9,
        stream=True
    ):
        yield output["choices"][0]["text"]
