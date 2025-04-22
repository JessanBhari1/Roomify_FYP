from django.db import models
from rooms.models import *

# Create your models here.
class ChatRoom(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_chats')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    latest_message = models.TextField(null=True, blank=True)
    has_unread_messages = models.BooleanField(default=False)
    customer_deleted = models.BooleanField(default=False)
    seller_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('room', 'customer', 'seller')

    def mark_as_read(self, for_user):
        """Precisely mark messages as read for the other user"""
        other_user = self.seller if for_user == self.customer else self.customer
        
        # Only mark the other user's unread messages
        updated = self.messages.filter(
            sender=other_user,
            read=False
        ).update(read=True)
        
        # Update room status if needed
        if updated > 0 or self.has_unread_messages:
            self.has_unread_messages = False
            self.save()
            return True
        return False
    
    def update_unread_status(self):
        """
        More robust unread status that persists across refreshes.
        Uses the actual message read status rather than just the flag.
        """
        # Get the other user in the conversation
        other_user = self.seller if hasattr(self, 'user') and self.user == self.customer else self.customer
        
        # Check for any unread messages from the other user
        has_unread = self.messages.filter(
            sender=other_user,
            read=False
        ).exists()
        
        # Update the flag if needed
        if self.has_unread_messages != has_unread:
            self.has_unread_messages = has_unread
            self.save()
        
        return has_unread

    def update_latest_message(self, message, sender):
        self.latest_message = message
        self.has_unread_messages = self.customer != sender and self.seller != sender
        self.save()
        return self

    def __str__(self):
        return f"Chat about {self.room.title}"

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.sender.email}: {self.message[:20]}..."