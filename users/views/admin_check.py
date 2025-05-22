from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ..permissions import IsCustomAdmin

@api_view(['GET'])
@permission_classes([IsCustomAdmin])
def test_admin_permission(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "authenticated": user.is_authenticated,
    })

