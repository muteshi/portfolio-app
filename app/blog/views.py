from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Category, Tag, Post

from blog import serializers


class MainBlogAppViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    """
    Base viewset for user owned blog attributes
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Return objects for the current authenticated  user
        """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """
        Create a new object
        """
        serializer.save(
            user=self.request.user
        )


class TagViewSet(MainBlogAppViewSet):
    """
    Manage tags in the database
    """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class CategoryViewSet(MainBlogAppViewSet):
    """
    Manage categories in the database
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    Manage posts in the database
    """
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    def _params_to_ints(self, qs):
        """
        Function to convert a list of string IDs to list of integers
        """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """
        Retrieve posts that are specific to logged in user
        Filter posts accordingly
        """
        tags = self.request.query_params.get('tags')
        cats = self.request.query_params.get('cats')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if cats:
            cat_ids = self._params_to_ints(cats)
            queryset = queryset.filter(category__id__in=cat_ids)

        return queryset.filter(
            author=self.request.user
        )

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        """
        if self.action == 'retrieve':
            return serializers.PostDetailSerializer
        elif self.action == 'upload_image':
            return serializers.PostImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new post and assign the logged in user
        """
        serializer.save(author=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None, slug=None):
        """
        Upload an image to a post
        """
        post = self.get_object()
        serializer = self.get_serializer(
            post,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )