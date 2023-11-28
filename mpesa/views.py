from django.http import JsonResponse
from rest_framework.decorators import api_view
from .services import get_oauth_token, stk_push, register_url, express_callback, b2c, b2c_callback

@api_view(['GET'])
def get_auth_token(request):
    token = get_oauth_token()
    return JsonResponse(token, safe=False)

@api_view(['POST'])
def stk_push_view(request):
    data = request.data
    response = stk_push(data)
    return JsonResponse(response, safe=False)

@api_view(['POST'])
def register_url_view(request):
    response = register_url()
    return JsonResponse(response)

@api_view(['POST'])
def express_callback_view(request):
    data = request.data
    response = express_callback(data)
    return JsonResponse(response)

@api_view(['POST'])
def b2c_view(request):
    data = request.data
    response = b2c(data)
    return JsonResponse(response)

@api_view(['POST'])
def b2c_callback_view(request):
    data = request.data
    response = b2c_callback(data)
    return JsonResponse(response)

@api_view(['POST'])
def b2c_queue_view(request):
    data = request.data
    response = b2c_callback(data)  # Assuming same logic as b2c_callback
    return JsonResponse(response)

@api_view(['POST'])
def c2b_callback_view(request):
    data = request.data
    response = b2c_callback(data)  # Modify as needed for C2B logic
    return JsonResponse(response)
