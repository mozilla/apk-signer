from django import http


def index(request):
    return http.HttpResponse(content='The APK Service is running!',
                             content_type='text/plain', status=200)
