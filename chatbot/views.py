import json
import uuid

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import ChatMessage
from .services import generate_bot_reply


@ensure_csrf_cookie
def chat_page(request):
    if not request.session.session_key:
        request.session.save()
    conversation_id = request.session.get("chat_conversation_id")
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        request.session["chat_conversation_id"] = conversation_id
    return render(request, "chatbot/chat.html")


@require_GET
def chat_history(request):
    if not request.session.session_key:
        request.session.save()
    conversation_id = request.session.get("chat_conversation_id")
    if not conversation_id:
        return JsonResponse({"messages": []})

    conv_uuid = uuid.UUID(conversation_id)
    qs = ChatMessage.objects.filter(conversation_id=conv_uuid).order_by("created_at")
    messages = [
        {
            "sender": m.sender,
            "message": m.message,
            "timestamp": timezone.localtime(m.created_at).isoformat(timespec="minutes")[:16].replace("T", " "),
        }
        for m in qs[:60]
    ]
    return JsonResponse({"messages": messages})


@require_POST
def chat_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        payload = {}

    user_message = (payload.get("message") or "").strip()

    if not request.session.session_key:
        request.session.save()
    conversation_id = request.session.get("chat_conversation_id")
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        request.session["chat_conversation_id"] = conversation_id

    conv_uuid = uuid.UUID(conversation_id)

    if user_message:
        ChatMessage.objects.create(
            conversation_id=conv_uuid,
            sender=ChatMessage.SENDER_USER,
            message=user_message,
        )

    bot_reply = generate_bot_reply(user_message)
    bot_message = ChatMessage.objects.create(
        conversation_id=conv_uuid,
        sender=ChatMessage.SENDER_BOT,
        message=bot_reply.text,
    )

    return JsonResponse(
        {
            "conversation_id": conversation_id,
            "reply": bot_reply.text,
            "timestamp": timezone.localtime(bot_message.created_at).isoformat(timespec="minutes"),
            "suggested_action": bot_reply.suggested_action,
        }
    )
