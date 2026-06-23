from django.http import HttpResponse


def placeholder(request):
    return HttpResponse("reports app is wired. models not created yet.")

