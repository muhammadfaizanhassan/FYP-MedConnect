# views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Conversation, ChatSession
from .modules.ai import AsklamaStream
from main.utils.audit_log import log_phi_access
import json
import uuid

def chat(request):
    error_message = ''
    
    # Get or create current session
    session_id = request.GET.get('session')
    if session_id:
        try:
            current_session = get_object_or_404(ChatSession, id=session_id)
            # Ensure user can only access their own sessions
            if request.user.is_authenticated and current_session.user != request.user:
                current_session = None
        except:
            current_session = None
    else:
        current_session = None
    
    # If no session, get or create the most recent session
    if not current_session:
        if request.user.is_authenticated:
            current_session = ChatSession.objects.filter(user=request.user).first()
        else:
            # For anonymous users, use session-based storage
            session_key = request.session.get('current_chat_session_id')
            if session_key:
                try:
                    current_session = ChatSession.objects.get(id=session_key)
                except ChatSession.DoesNotExist:
                    current_session = None
            
            if not current_session:
                current_session = ChatSession.objects.create(user=None)
                request.session['current_chat_session_id'] = str(current_session.id)
    
    # Get conversations for current session
    conversations = []
    if current_session:
        conversations = current_session.conversations.all().order_by('created_at')
    
    # Get all sessions for the sidebar
    if request.user.is_authenticated:
        all_sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')[:20]
    else:
        session_key = request.session.get('current_chat_session_id')
        all_sessions = []
        if session_key:
            try:
                session = ChatSession.objects.get(id=session_key)
                all_sessions = [session]
            except:
                pass
    
    return render(request, 'chat/chat.html', {
        'error_message': error_message,
        'current_session': current_session,
        'conversations': conversations,
        'all_sessions': all_sessions,
    })

@require_http_methods(["POST"])
def chat_stream(request):
    """Streaming endpoint for real-time AI responses"""
    prompt = request.POST.get('prompt', '').strip()
    session_id = request.POST.get('session_id', '').strip()
    
    if not prompt:
        return JsonResponse({'error': 'Please enter a valid prompt.'}, status=400)
    
    def generate():
        """Generator function for streaming responses"""
        full_response = ""
        try:
            # Get or create session
            if session_id:
                try:
                    chat_session = ChatSession.objects.get(id=session_id)
                    # Ensure user can only access their own sessions
                    if request.user.is_authenticated and chat_session.user != request.user:
                        chat_session = None
                except ChatSession.DoesNotExist:
                    chat_session = None
            else:
                chat_session = None
            
            if not chat_session:
                # Create new session
                chat_session = ChatSession.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    title=prompt[:50] + "..." if len(prompt) > 50 else prompt
                )
                if not request.user.is_authenticated:
                    request.session['current_chat_session_id'] = str(chat_session.id)
            
            # Stream the AI response
            for chunk in AsklamaStream(prompt, 2000):
                if chunk:
                    full_response += chunk
                    # Send chunk as JSON
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False, 'session_id': str(chat_session.id)})}\n\n"
            
            # Save the conversation after streaming is complete
            if full_response.strip():
                conversation = Conversation.objects.create(
                    session=chat_session,
                    prompt=prompt, 
                    response=full_response.strip()
                )
                
                # Update session title if it's the first message
                if chat_session.conversations.count() == 1:
                    chat_session.title = prompt[:50] + "..." if len(prompt) > 50 else prompt
                    chat_session.save()
                
                # Log PHI access for HIPAA compliance
                log_phi_access(
                    user=request.user if request.user.is_authenticated else None,
                    action='create',
                    resource_type='conversation',
                    resource_id=str(conversation.id),
                    request=request,
                    details={'prompt_length': len(prompt), 'response_length': len(full_response), 'session_id': str(chat_session.id)}
                )
                
                # Send final message
                yield f"data: {json.dumps({'chunk': '', 'done': True, 'conversation_id': conversation.id, 'session_id': str(chat_session.id)})}\n\n"
            else:
                yield f"data: {json.dumps({'error': 'No response generated. Please try again.', 'done': True})}\n\n"
                
        except Exception as e:
            print(f"Error during AI streaming: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': 'An error occurred while processing your request. Please try again.', 'done': True})}\n\n"
    
    response = StreamingHttpResponse(generate(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response

@require_http_methods(["POST"])
def new_session(request):
    """Create a new chat session"""
    session = ChatSession.objects.create(
        user=request.user if request.user.is_authenticated else None
    )
    if not request.user.is_authenticated:
        request.session['current_chat_session_id'] = str(session.id)
    return JsonResponse({'session_id': str(session.id), 'redirect': f'/chat/?session={session.id}'})

@require_http_methods(["POST"])
def delete_session(request, session_id):
    """Delete a chat session"""
    try:
        session = ChatSession.objects.get(id=session_id)
        # Ensure user can only delete their own sessions
        if request.user.is_authenticated and session.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        session.delete()
        return JsonResponse({'success': True})
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
