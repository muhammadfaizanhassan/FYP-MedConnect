from django.shortcuts import render
from .models import Conversation
from django.core.paginator import Paginator

def chat(request):
    response = ''
    error_message = ''

    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        if prompt:
            try:
                # Save the conversation in the database
                response = "Placeholder response for POST requests"
                Conversation.objects.create(prompt=prompt, response=response)
            except Exception as e:
                print(f"Error: {e}")
                error_message = "An error occurred while processing your request."
        else:
            error_message = "Please enter a valid prompt."

    conversations = Conversation.objects.all().order_by('-id')
    paginator = Paginator(conversations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'chat/chat.html', {
        'response': response,
        'error_message': error_message,
        'page_obj': page_obj
    })
