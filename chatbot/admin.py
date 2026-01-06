from django.contrib import admin

from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["created_at", "conversation_id", "sender", "short_message"]
    list_filter = ["sender", "created_at"]
    search_fields = ["message", "conversation_id"]
    readonly_fields = ["created_at"]

    @admin.display(description="Message")
    def short_message(self, obj: ChatMessage) -> str:
        return obj.message[:80]
