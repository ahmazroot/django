import json
import requests
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from apps.tenants.models import ChatMessage, CustomerData


@csrf_exempt
@require_http_methods(["POST"])
def chat_call(request):
    """
    Chat API endpoint that integrates with external AI API
    Identifies tenant via Host header and processes chat requests
    """

    # Check if tenant is identified
    if not hasattr(request, 'tenant') or not request.tenant:
        return JsonResponse({
            'error': 'Tenant not found or inactive',
            'message': 'Please check your domain configuration'
        }, status=404)

    tenant = request.tenant

    # Check token limits
    if not tenant.has_tokens_available():
        return JsonResponse({
            'error': 'Token limit exceeded',
            'message': f'Tenant has used {tenant.token_usage}/{tenant.token_limit} tokens'
        }, status=429)

    try:
        # Parse request data
        data = json.loads(request.body)
        user_prompt = data.get('prompt', '').strip()

        if not user_prompt:
            return JsonResponse({
                'error': 'Missing prompt',
                'message': 'Please provide a prompt in the request body'
            }, status=400)

        # Optional parameters
        model = data.get('model', 'gpt-3.5-turbo')
        seed = data.get('seed', None)
        customer_id = data.get('customer_id', None)

        # Get customer data if provided
        customer_data = None
        specific_customer_context = ""
        if customer_id:
            try:
                customer_data = CustomerData.objects.get(
                    id=customer_id,
                    tenant=tenant
                )
                # Prepare context for the specific customer if found
                if customer_data:
                    specific_customer_context += f"\n\nSpecific Customer Context:\n"
                    specific_customer_context += f"Customer Name: {customer_data.customer_name}\n"
                    if customer_data.customer_email:
                        specific_customer_context += f"Customer Email: {customer_data.customer_email}\n"
                    if customer_data.customer_phone:
                        specific_customer_context += f"Customer Phone: {customer_data.customer_phone}\n"
                    if customer_data.data and isinstance(customer_data.data, dict) and customer_data.data:
                        specific_customer_context += f"Customer Additional Data: {json.dumps(customer_data.data, indent=2)}\n"

            except CustomerData.DoesNotExist:
                pass

        # Build system message with tenant data
        tenant_data_context = ""
        if tenant.name:
            tenant_data_context += f"Company: {tenant.name}\n"

        # Get recent customer data for context
        recent_customers = CustomerData.objects.filter(tenant=tenant).order_by('-created_at')[:5]
        if recent_customers:
            tenant_data_context += "Recent customers and their data:\n"
            for customer in recent_customers:
                tenant_data_context += f"- Customer: {customer.customer_name}"
                if customer.customer_email:
                    tenant_data_context += f" (Email: {customer.customer_email})"
                if customer.customer_phone:
                    tenant_data_context += f" (Phone: {customer.customer_phone})"

                # Include the JSONField data (this is the main customer data)
                if customer.data and isinstance(customer.data, dict) and customer.data:
                    tenant_data_context += f"\n  Customer Data: {json.dumps(customer.data, indent=2)}"

                tenant_data_context += "\n"

        # Combine tenant behavior with tenant data
        system_content = tenant.system_parameter
        if tenant_data_context:
            system_content += f"\n\nTenant Data Context:\n{tenant_data_context}"
        if specific_customer_context:
            system_content += specific_customer_context

        # Prepare external API call
        external_api_url = f"https://text.uuuuai.ai/{user_prompt}"
        api_payload = {
            'prompt': user_prompt,
            'system': system_content,  # Use combined system content
            'model': model
        }

        if seed:
            api_payload['seed'] = seed

        # Make API call and measure response time
        start_time = time.time()

        try:
            # Make request to external AI API
            response = requests.post(
                external_api_url,
                json=api_payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                ai_response = response.text
            else:
                ai_response = f"API Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            ai_response = f"Connection Error: {str(e)}"

        # Store chat message in database
        chat_message = ChatMessage.objects.create(
            tenant=tenant,
            customer_data=customer_data,
            user_prompt=user_prompt,
            ai_response=ai_response,
            tokens_used=1,  # You can implement token counting logic here
            model_used=model,
            seed_used=str(seed) if seed else None,
            response_time_ms=response_time_ms
        )

        # Update tenant token usage
        tenant.increment_token_usage(1)

        # Return response
        return JsonResponse({
            'success': True,
            'message_id': str(chat_message.id),
            'prompt': user_prompt,
            'response': ai_response,
            'model': model,
            'response_time_ms': response_time_ms,
            'tokens_remaining': tenant.token_limit - tenant.token_usage,
            'tenant': tenant.name
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON',
            'message': 'Please provide valid JSON in the request body'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def chat_history(request):
    """
    Get chat history for the current tenant
    """
    if not hasattr(request, 'tenant') or not request.tenant:
        return JsonResponse({
            'error': 'Tenant not found or inactive'
        }, status=404)

    tenant = request.tenant

    # Get query parameters for pagination
    limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 messages
    offset = int(request.GET.get('offset', 0))

    # Get chat messages for this tenant only
    messages = ChatMessage.objects.filter(tenant=tenant)[offset:offset+limit]

    messages_data = []
    for message in messages:
        messages_data.append({
            'id': str(message.id),
            'prompt': message.user_prompt,
            'response': message.ai_response,
            'created_at': message.created_at.isoformat(),
            'model': message.model_used,
            'tokens_used': message.tokens_used,
            'response_time_ms': message.response_time_ms
        })

    return JsonResponse({
        'success': True,
        'messages': messages_data,
        'total_messages': ChatMessage.objects.filter(tenant=tenant).count(),
        'tenant': tenant.name,
        'tokens_used': tenant.token_usage,
        'tokens_limit': tenant.token_limit
    })


@csrf_exempt
@require_http_methods(["POST"])
def add_customer_data(request):
    """
    Add customer data for the current tenant
    """
    if not hasattr(request, 'tenant') or not request.tenant:
        return JsonResponse({
            'error': 'Tenant not found or inactive'
        }, status=404)

    tenant = request.tenant

    try:
        data = json.loads(request.body)

        customer_name = data.get('name', '').strip()
        customer_email = data.get('email', '').strip()
        customer_phone = data.get('phone', '').strip()
        additional_data = data.get('data', {})

        if not customer_name:
            return JsonResponse({
                'error': 'Missing customer name',
                'message': 'Customer name is required'
            }, status=400)

        # Create customer data
        customer_data = CustomerData.objects.create(
            tenant=tenant,
            customer_name=customer_name,
            customer_email=customer_email if customer_email else None,
            customer_phone=customer_phone if customer_phone else None,
            data=additional_data
        )

        return JsonResponse({
            'success': True,
            'customer_id': str(customer_data.id),
            'name': customer_data.customer_name,
            'email': customer_data.customer_email,
            'phone': customer_data.customer_phone,
            'created_at': customer_data.created_at.isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON',
            'message': 'Please provide valid JSON in the request body'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tenant_info(request):
    """
    Get current tenant information
    """
    if not hasattr(request, 'tenant') or not request.tenant:
        return JsonResponse({
            'error': 'Tenant not found or inactive'
        }, status=404)

    tenant = request.tenant

    return JsonResponse({
        'success': True,
        'tenant': {
            'id': str(tenant.id),
            'name': tenant.name,
            'domain': tenant.domain,
            'tokens_used': tenant.token_usage,
            'tokens_limit': tenant.token_limit,
            'tokens_remaining': tenant.token_limit - tenant.token_usage,
            'system_parameter': tenant.system_parameter,
            'created_at': tenant.created_at.isoformat()
        }
    })