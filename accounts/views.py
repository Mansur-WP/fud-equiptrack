from django.http import HttpResponse


def placeholder(request):
    return HttpResponse("accounts app is wired. models not created yet.")

