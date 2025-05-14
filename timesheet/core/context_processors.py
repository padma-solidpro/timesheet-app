from .models import Resource  # or wherever your Resource model is

def access_level_context(request):
    if request.user.is_authenticated:
        try:
            resource = Resource.objects.get(user=request.user)
            return {'user_access_level': resource.role.access_level}
        except Resource.DoesNotExist:
            return {'user_access_level': None}
    return {'user_access_level': None}
