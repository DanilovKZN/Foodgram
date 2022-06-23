from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import filters, viewsets, status, mixins
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from .models import CustomUser
from .serializers import UserSerializer
from .permissions import IsAuthorOrAdminReadOnly


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthorOrAdminReadOnly,)
    #filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['username']

    
    @action(
        methods=('GET', 'PATCH',),
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = self.get_serializer(
            request.user,
            data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK)
