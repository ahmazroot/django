
from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=100, unique=True)
    system_parameter = models.TextField(
        help_text="System parameter used for AI API calls",
        default="You are a helpful customer service assistant."
    )
    token_limit = models.IntegerField(
        default=1000,
        validators=[MinValueValidator(0)]
    )
    token_usage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.domain})"
    
    def has_tokens_available(self):
        return self.token_usage < self.token_limit
    
    def increment_token_usage(self, tokens=1):
        self.token_usage += tokens
        self.save(update_fields=['token_usage'])


class CustomerData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='customer_data')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=50, blank=True, null=True)
    data = models.JSONField(default=dict, help_text="Additional customer data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Customer Data"
    
    def __str__(self):
        return f"{self.customer_name} - {self.tenant.name}"


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='chat_messages')
    customer_data = models.ForeignKey(
        CustomerData, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='chat_messages'
    )
    user_prompt = models.TextField()
    ai_response = models.TextField(blank=True, null=True)
    tokens_used = models.IntegerField(default=1)
    model_used = models.CharField(max_length=100, blank=True, null=True)
    seed_used = models.CharField(max_length=100, blank=True, null=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat - {self.tenant.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
