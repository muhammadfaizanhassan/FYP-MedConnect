from llama_cpp import Llama
lama=Llama(model_path="C:\\Users\\pc\\OneDrive\\Desktop\\models\\llamaModel.gguf",verbose=True,n_gpu_layers=30)

def Asklama(prompt,tokens):
    output=lama(prompt,max_tokens=tokens)
    print(output,prompt)
    return output["choices"][0]['text']




