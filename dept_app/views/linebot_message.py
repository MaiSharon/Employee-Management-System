from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dept_app.tasks.linebot_tasks import send_greeting_task


@csrf_exempt
def send_greeting_view(request):
    if request.method == 'POST':
        user_id = 'Ue04e12493a401b2a9768786f1ca89e3b'  # Replace with the actual user ID
        message = "我又來了"
        send_greeting_task.delay(user_id, message)
        return JsonResponse({'status': 'ok'})
