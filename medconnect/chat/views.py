from django.shortcuts import render
from .models import Conversation
from .modules.ai import Asklama
from django.core.paginator import Paginator

def chat(request):
    response = ''
    error_message = ''
    
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()  # Get and strip whitespace
        
        if prompt:
            try:
                # Run the AI model
                output = Asklama(f"Q: {prompt} A: ", 2000)
                response = ' '.join(output).strip()
                
                if response:
                    # Save the conversation in the database
                    Conversation.objects.create(prompt=prompt, response=response)
                else:
                    error_message = "No response generated. Please try again."
            except Exception as e:
                error_message = "An error occurred while processing your request. Please try again."
        else:
            error_message = "Please enter a valid prompt."
    
    # Retrieve the latest conversations from the database with pagination
    conversations = Conversation.objects.all().order_by('-id')
    paginator = Paginator(conversations, 10)  # Show 10 conversations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'chat/chat.html', {
        'response': response,
        'error_message': error_message,
        'page_obj': page_obj
    })
