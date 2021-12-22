from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from rest_framework.generics import CreateAPIView

from core.utils import caching, id_generator
from core.models import Category, Message, Portfolio, Resume, Skill, Tag, Post

from blog import serializers


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


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
    http_method_names = ['get', 'head']

    def get_queryset(self):
        """
        Return objects for the current authenticated  user
        """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(post__isnull=False)

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


class ResumeViewSet(viewsets.ModelViewSet):
    """
    Manage resume
    """
    queryset = Resume.objects.all()
    serializer_class = serializers.ResumeSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'head']


class SkillViewSet(viewsets.ModelViewSet):
    """
    Manage skill
    """
    queryset = Skill.objects.all()
    serializer_class = serializers.SkillSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'head']


class CategoryViewSet(MainBlogAppViewSet):
    """
    Manage categories in the database
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class MessageCreateAPIView(CreateAPIView):
    """Create a new message object"""
    queryset = Message.objects.all()
    serializer_class = serializers.MessageSerializer

    def perform_create(self, serializer):
        serializer.save(message_id=id_generator(Message))


class PostViewSet(viewsets.ModelViewSet):
    """
    Manage posts in the database
    """
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    http_method_names = ['get', 'head']

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
            try:
                tag_ids = self._params_to_ints(tags)
                queryset = queryset.filter(tags__id__in=tag_ids)
            except ValueError:
                queryset = queryset.filter(
                    tags__name__icontains=tags.lower())

        if cats:
            try:
                cat_ids = self._params_to_ints(cats)
                queryset = queryset.filter(category__id__in=cat_ids)
            except ValueError:
                queryset = queryset.filter(
                    category__name__icontains=cats.lower())
        return queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        """
        if self.action == 'retrieve':
            return serializers.PostDetailSerializer
        elif self.action == 'upload_image':
            return serializers.PostImageSerializer

        return self.serializer_class

    def retrieve(self, request, pk=None, slug=None):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, slug=slug)
        serializer = serializers.PostDetailSerializer(post)
        caching(slug, serializer.data)
        return Response(serializer.data)

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


class PortfolioViewSet(PostViewSet):
    """
    Manages portfolio objects
    """
    queryset = Portfolio.objects.all()
    serializer_class = serializers.PortfolioSerializer
