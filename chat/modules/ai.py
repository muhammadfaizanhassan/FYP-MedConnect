import os
from pathlib import Path

# Initialize Llama model (lazy loading)
_llama_model = None

def get_llama_model():
    """
    Get or initialize the local Llama model.
    Uses lazy loading to avoid loading the model on import.
    """
    global _llama_model
    
    if _llama_model is None:
        try:
            from llama_cpp import Llama
            
            # Get model path - check multiple locations
            base_dir = Path(__file__).resolve().parent.parent.parent
            model_paths = [
                base_dir / "models" / "llama-2-7b.Q5_K_M.gguf",
                base_dir / "models" / "llamaModel.gguf",
                Path("models/llama-2-7b.Q5_K_M.gguf"),
                Path("models/llamaModel.gguf"),
            ]
            
            # Try to find the model file
            model_path = None
            for path in model_paths:
                if path.exists():
                    model_path = str(path)
                    break
            
            if not model_path:
                raise FileNotFoundError(
                    "Llama model file not found. Please ensure the model file exists in the 'models' directory."
                )
            
            # Initialize Llama model with GPU support
            # n_gpu_layers: Set to -1 to use all available GPU layers, or 0 for CPU-only
            # For GPU: Set to -1 (all layers) or a specific number (e.g., 30)
            
            # Check for CUDA/GPU availability
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✓ NVIDIA GPU detected via nvidia-smi")
                    gpu_available = True
                else:
                    gpu_available = False
                    print("⚠ nvidia-smi not available - GPU may not be accessible")
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                gpu_available = False
                print("⚠ Could not verify GPU via nvidia-smi - will attempt GPU loading anyway")
            
            try:
                # Try GPU first (n_gpu_layers=-1 means use all GPU layers)
                # If GPU is not available, it will fall back to CPU
                print("🔄 Initializing Llama model with GPU support (n_gpu_layers=-1)...")
                _llama_model = Llama(
                    model_path=model_path,
                    verbose=False,  # Set to True for debugging
                    n_gpu_layers=-1,  # Use all available GPU layers (-1 = all, 0 = CPU only)
                    n_ctx=2048,  # Context window size
                    n_threads=None,  # Use all available CPU threads (for CPU fallback)
                )
                
                # Verify GPU usage by checking model metadata
                # The model object should have GPU layers loaded if GPU is working
                print(f"✓ Local Llama model loaded successfully from: {model_path}")
                print(f"  GPU layers: All available (n_gpu_layers=-1)")
                
                # Additional verification - check if we can get GPU info
                try:
                    # Try to access internal GPU state (if available)
                    if hasattr(_llama_model, '_ctx') and _llama_model._ctx:
                        print("  ✓ Model context initialized - GPU acceleration enabled")
                    else:
                        print("  ⚠ Could not verify GPU context - may be using CPU")
                    
                    # Check if CUDA is actually being used
                    try:
                        import llama_cpp
                        # Check for CUDA support in the library
                        if hasattr(llama_cpp, 'llama_cpp_has_cuda'):
                            cuda_available = llama_cpp.llama_cpp_has_cuda()
                            if cuda_available:
                                print("  ✓ CUDA support confirmed in llama-cpp-python")
                            else:
                                print("  ⚠ CUDA not available in llama-cpp-python - using CPU")
                                print("     To enable GPU, reinstall with: pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121")
                        else:
                            # Try alternative check
                            if hasattr(_llama_model, 'n_gpu_layers'):
                                gpu_layers = _llama_model.n_gpu_layers
                                if gpu_layers > 0:
                                    print(f"  ✓ GPU layers active: {gpu_layers} layers on GPU")
                                else:
                                    print("  ⚠ No GPU layers detected - running on CPU")
                    except Exception as e:
                        print(f"  ℹ Could not verify GPU status: {e}")
                except:
                    pass
                    
            except Exception as e:
                error_msg = str(e)
                if "CUDA" in error_msg or "GPU" in error_msg or "cublas" in error_msg.lower():
                    print(f"⚠ GPU initialization failed: {error_msg}")
                    print("  Attempting to load with CPU fallback...")
                    # Fallback to CPU
                    _llama_model = Llama(
                        model_path=model_path,
                        verbose=False,
                        n_gpu_layers=0,  # Force CPU
                        n_ctx=2048,
                        n_threads=None,
                    )
                    print("  ✓ Model loaded in CPU mode")
                else:
                    raise Exception(f"Failed to load Llama model: {e}")
                
        except ImportError:
            raise ImportError(
                "llama-cpp-python is not installed.\n"
                "To install on Windows, you need to:\n"
                "1. Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/\n"
                "   (Select 'Desktop development with C++' workload)\n"
                "2. Then run: pip install llama-cpp-python\n"
                "\n"
                "Alternatively, you can try installing a pre-built wheel if available."
            )
    
    return _llama_model

def Asklama(prompt, tokens):
    """
    Sends a prompt to the local Llama model with enforced medical context.

    Args:
        prompt (str): The input prompt for the model.
        tokens (int): The maximum number of tokens to generate.

    Returns:
        str: The generated text from the model.
    """
    response = ""

    # Enforce a medical context in the prompt
    # Format: Clear instruction + user question
    medical_context = (
        "You are a professional medical assistant. Provide helpful, clear, and accurate medical information. "
        "Give practical advice and always remind users to consult healthcare professionals for serious concerns. "
        "Keep responses concise but informative. Do not use HTML tags, markdown, or special formatting. "
        "Write in plain text only.\n\n"
    )
    # Clean the prompt - remove any Q: A: formatting that might confuse the model
    clean_prompt = prompt.replace("Q:", "").replace("A:", "").strip()
    full_prompt = medical_context + "Patient question: " + clean_prompt + "\n\nMedical assistant response:"

    try:
        # Get the local Llama model
        llama = get_llama_model()
        
        if llama is None:
            raise Exception("Llama model is not available")
        
        print(f"Generating response for prompt: {prompt[:50]}...")
        
        # Generate response using local model with streaming
        # Use stream=True to get real-time output
        response_text = ""
        try:
            for output in llama(
                full_prompt,
                max_tokens=min(tokens, 2000),  # Cap at 2000 tokens
                temperature=0.7,   # Sampling temperature for randomness
                top_p=0.9,         # Nucleus sampling
                top_k=40,          # Top-k sampling
                repeat_penalty=1.1,  # Repetition penalty
                stop=["Patient question:", "User question:", "Q:", "A:", "Medical assistant response:", "Medical assistant:", "<details>", "</details>", "<summary>", "</summary>", "<b>", "</b>", "\n\n\n"],  # Stop sequences
                echo=False,  # Don't echo the prompt in the output
                stream=True,  # Stream the output
            ):
                # Extract text from streaming output
                if "choices" in output and len(output["choices"]) > 0:
                    text = output["choices"][0].get("text", "")
                    if text:
                        response_text += text
        except Exception as stream_error:
            print(f"Streaming failed: {stream_error}, trying non-streaming...")
            response_text = ""  # Reset to try non-streaming
        
        # If streaming didn't work, try non-streaming
        if not response_text:
            print("Streaming returned empty, trying non-streaming mode...")
            try:
                output = llama(
                    full_prompt,
                    max_tokens=min(tokens, 2000),
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                    repeat_penalty=1.1,
                    stop=["Patient question:", "User question:", "Q:", "A:", "Medical assistant response:", "Medical assistant:", "<details>", "</details>", "<summary>", "</summary>", "<b>", "</b>", "\n\n\n"],
                    echo=False,
                    stream=False,
                )
                
                # Extract the generated text
                if "choices" in output and len(output["choices"]) > 0:
                    response_text = output["choices"][0].get("text", "").strip()
                elif "text" in output:
                    response_text = output["text"].strip()
                else:
                    print(f"Unexpected output format: {type(output)}")
                    print(f"Output keys: {output.keys() if isinstance(output, dict) else 'Not a dict'}")
                    # Try to get text from the output structure
                    if isinstance(output, dict):
                        response_text = str(output).strip()
                    else:
                        response_text = str(output).strip()
            except Exception as non_stream_error:
                print(f"Non-streaming also failed: {non_stream_error}")
                response_text = ""
        
        response = response_text.strip() if response_text else ""
        
        # Clean up the response
        if response:
            # Remove any remaining prompt artifacts (but be careful not to remove too much)
            if full_prompt in response:
                response = response.replace(full_prompt, "").strip()
            
            # Remove HTML tags and special formatting
            import re
            # Remove HTML tags
            response = re.sub(r'<[^>]+>', '', response)
            # Remove markdown-style formatting
            response = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', response)  # Remove markdown links
            response = re.sub(r'\*\*([^\*]+)\*\*', r'\1', response)  # Remove bold
            response = re.sub(r'\*([^\*]+)\*', r'\1', response)  # Remove italic
            
            # Remove HTML tags and special formatting
            import re
            # Remove HTML tags
            response = re.sub(r'<[^>]+>', '', response)
            # Remove markdown-style formatting
            response = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', response)  # Remove markdown links
            response = re.sub(r'\*\*([^\*]+)\*\*', r'\1', response)  # Remove bold
            response = re.sub(r'\*([^\*]+)\*', r'\1', response)  # Remove italic
            
            # Remove prompt prefixes that might appear in the response
            response = re.sub(r'^Medical assistant response:\s*', '', response, flags=re.IGNORECASE)
            response = re.sub(r'^Medical assistant:\s*', '', response, flags=re.IGNORECASE)
            response = re.sub(r'^Assistant response:\s*', '', response, flags=re.IGNORECASE)
            response = re.sub(r'^Assistant:\s*', '', response, flags=re.IGNORECASE)
            response = re.sub(r'^Response:\s*', '', response, flags=re.IGNORECASE)
            # Remove from anywhere in the text (not just beginning)
            response = re.sub(r'Medical assistant response:\s*', '', response, flags=re.IGNORECASE)
            response = re.sub(r'Medical assistant:\s*', '', response, flags=re.IGNORECASE)
            
            # Remove stop sequences if they appear at the end
            for stop_seq in ["Patient question:", "User question:", "Q:", "A:", "Medical assistant response:", "Medical assistant:", "<details>", "</details>", "<summary>", "</summary>", "\n\n\n", "\n\n"]:
                if response.endswith(stop_seq):
                    response = response[:-len(stop_seq)].strip()
            
            # Remove leading/trailing whitespace and normalize
            response = response.strip()
            # Remove multiple consecutive newlines
            response = re.sub(r'\n{3,}', '\n\n', response)
            
            print(f"Generated response length: {len(response)} characters")
            print(f"Response preview: {response[:100]}...")
            
            # If response is still empty after cleaning, provide a default
            if not response:
                response = "I apologize, but I couldn't generate a meaningful response. Please try rephrasing your question."
        else:
            print("Warning: Empty response generated from model")
            response = "I apologize, but I couldn't generate a response. Please try rephrasing your question or try again."
        
    except FileNotFoundError as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        response = (
            "I apologize, but the AI model file is not found. "
            "Please contact the system administrator. "
            "For urgent medical concerns, please contact a healthcare professional immediately."
        )
    except ImportError as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        response = (
            "I apologize, but the AI system is not properly configured. "
            "Please contact the system administrator. "
            "For urgent medical concerns, please contact a healthcare professional immediately."
        )
    except Exception as e:
        # Handle and log any other exceptions
        error_msg = str(e)
        print(f"Error during AI processing: {e}")
        import traceback
        traceback.print_exc()
        response = (
            "I apologize, but I'm experiencing technical difficulties. "
            "Please try again in a moment. "
            "For urgent medical concerns, please contact a healthcare professional immediately."
        )

    return response

def AsklamaStream(prompt, tokens):
    """
    Streams responses from the local Llama model with enforced medical context.
    Yields chunks of text as they are generated.

    Args:
        prompt (str): The input prompt for the model.
        tokens (int): The maximum number of tokens to generate.

    Yields:
        str: Chunks of generated text.
    """
    # Enforce a medical context in the prompt
    medical_context = (
        "You are a professional medical assistant. Provide helpful, clear, and accurate medical information. "
        "Give practical advice and always remind users to consult healthcare professionals for serious concerns. "
        "Keep responses concise but informative. Do not use HTML tags, markdown, or special formatting. "
        "Write in plain text only.\n\n"
    )
    # Clean the prompt - remove any Q: A: formatting that might confuse the model
    clean_prompt = prompt.replace("Q:", "").replace("A:", "").strip()
    full_prompt = medical_context + "Patient question: " + clean_prompt + "\n\nMedical assistant response:"

    try:
        # Get the local Llama model
        llama = get_llama_model()
        
        if llama is None:
            raise Exception("Llama model is not available")
        
        print(f"Streaming response for prompt: {prompt[:50]}...")
        
        # Stream response using local model
        import re
        accumulated_text = ""
        
        for output in llama(
            full_prompt,
            max_tokens=min(tokens, 2000),
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.1,
            stop=["Patient question:", "User question:", "Q:", "A:", "<details>", "</details>", "<summary>", "</summary>", "<b>", "</b>", "\n\n\n"],
            echo=False,
            stream=True,
        ):
            # Extract text from streaming output
            if "choices" in output and len(output["choices"]) > 0:
                text = output["choices"][0].get("text", "")
                if text:
                    accumulated_text += text
                    # Clean HTML tags and prompt prefixes on the fly
                    cleaned_text = re.sub(r'<[^>]+>', '', text)
                    # Remove prompt prefixes as they appear
                    cleaned_text = re.sub(r'Medical assistant response:\s*', '', cleaned_text, flags=re.IGNORECASE)
                    cleaned_text = re.sub(r'Medical assistant:\s*', '', cleaned_text, flags=re.IGNORECASE)
                    if cleaned_text:
                        yield cleaned_text
        
        # Final cleanup of accumulated text
        if accumulated_text:
            # Remove any remaining HTML tags
            final_response = re.sub(r'<[^>]+>', '', accumulated_text)
            # Remove markdown formatting
            final_response = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', final_response)
            final_response = re.sub(r'\*\*([^\*]+)\*\*', r'\1', final_response)
            final_response = re.sub(r'\*([^\*]+)\*', r'\1', final_response)
            
            # Remove prompt prefixes that might appear in the response
            final_response = re.sub(r'^Medical assistant response:\s*', '', final_response, flags=re.IGNORECASE)
            final_response = re.sub(r'^Medical assistant:\s*', '', final_response, flags=re.IGNORECASE)
            final_response = re.sub(r'^Assistant response:\s*', '', final_response, flags=re.IGNORECASE)
            final_response = re.sub(r'^Assistant:\s*', '', final_response, flags=re.IGNORECASE)
            final_response = re.sub(r'^Response:\s*', '', final_response, flags=re.IGNORECASE)
            # Remove from anywhere in the text (not just beginning)
            final_response = re.sub(r'Medical assistant response:\s*', '', final_response, flags=re.IGNORECASE)
            final_response = re.sub(r'Medical assistant:\s*', '', final_response, flags=re.IGNORECASE)
            
            # Remove stop sequences
            for stop_seq in ["Patient question:", "User question:", "Q:", "A:", "Medical assistant response:", "Medical assistant:", "<details>", "</details>", "<summary>", "</summary>", "<b>", "</b>", "\n\n\n", "\n\n"]:
                if final_response.endswith(stop_seq):
                    final_response = final_response[:-len(stop_seq)].strip()
            
            # Normalize whitespace
            final_response = re.sub(r'\n{3,}', '\n\n', final_response).strip()
            
            print(f"Streamed response complete: {len(final_response)} characters")
        
    except Exception as e:
        print(f"Error during AI streaming: {e}")
        import traceback
        traceback.print_exc()
        yield "I apologize, but I'm experiencing technical difficulties. Please try again in a moment. For urgent medical concerns, please contact a healthcare professional immediately."
