from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# @method_decorator(csrf_exempt, name='dispatch')
# class HelloView(View):
#     def get(self, request, *args, **kwargs):
#         name = request.GET.get("name", "unknown")
#         data = {"message": f"你好，{name}"}
#         print(request)
#         print("接收到 AJAX 请求：")
#         print("GET 参数：", request.GET)
#         return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
