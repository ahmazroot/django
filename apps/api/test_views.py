
from django.shortcuts import render
from django.http import HttpResponse


def test_chat_interface(request):
    """
    Simple test interface for the chat API
    """
    with open('templates/test_chat.html', 'r') as f:
        html_content = f.read()
    return HttpResponse(html_content, content_type='text/html')
