from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination

from .models import CustomUser, Subscribe
from .permissions import IsAuthenOrAuthorOrAdminReadOnly
from .serializers import SubscribeSerializer, UserSerializer


SUB_ERROR = 'Вы уже подписаны или пытаетесь подписаться на самого себя'


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenOrAuthorOrAdminReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
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

    @action(
        methods=(['post', 'delete']),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Проверяемся - подписываемся/отписываемся."""
        author = get_object_or_404(CustomUser, id=self.kwargs.get('id'))
        if request.method == "POST":
            if_already_exists = Subscribe.objects.filter(
                author=author, user=request.user
            ).exists()
            if if_already_exists or request.user == author:
                return Response({
                    'errors': SUB_ERROR},
                    status=status.HTTP_400_BAD_REQUEST
                )
            new_subscribe = Subscribe.objects.create(
                author=author,
                user=request.user
            )
            serializer = SubscribeSerializer(
                new_subscribe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            our_subscribe = Subscribe.objects.filter(
                user=request.user,
                author=author
            )
            if our_subscribe:
                our_subscribe.delete()
                return Response(
                    {"Оповещение": "Пользователь удален из подписок!"},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {"Ошибка": "Такого пользователя нет в подписчиках!"},
                    status=status.HTTP_400_BAD_REQUEST
                )


class SubscriptionsList(ListAPIView):
    """Список подписчиков."""
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)
