from django.db import models


class ChatMessage(models.Model):
    SENDER_USER = "user"
    SENDER_BOT = "bot"

    SENDER_CHOICES = [
        (SENDER_USER, "User"),
        (SENDER_BOT, "Bot"),
    ]

    conversation_id = models.UUIDField(db_index=True)
    sender = models.CharField(max_length=8, choices=SENDER_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.sender}: {self.message[:48]}"
