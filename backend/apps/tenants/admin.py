
from django.contrib import admin
from .models import Tenant, CustomerData, ChatMessage


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'token_usage', 'token_limit', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'domain']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'domain', 'is_active')
        }),
        ('API Configuration', {
            'fields': ('system_parameter', 'token_limit', 'token_usage')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(CustomerData)
class CustomerDataAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'customer_email', 'tenant', 'created_at']
    list_filter = ['tenant', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'tenant__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'user_prompt_preview', 'tokens_used', 'model_used', 'created_at']
    list_filter = ['tenant', 'model_used', 'created_at']
    search_fields = ['tenant__name', 'user_prompt', 'ai_response']
    readonly_fields = ['id', 'created_at']
    
    @admin.display(description='Prompt Preview')
    def user_prompt_preview(self, obj):
        return obj.user_prompt[:50] + '...' if len(obj.user_prompt) > 50 else obj.user_prompt
