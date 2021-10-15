from rest_framework import serializers

from core.models import Tag, Category, Post


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer class for tag object
    """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer class for category object
    """

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_Fields = ('id',)

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer class for post object
    """
    category = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'date_posted', 'updated',
                  'category', 'tags','slug')
        read_only_Fields = ('id','date_posted','updated')
        


class PostDetailSerializer(PostSerializer):
    """
    Serializer class for post object details view
    """
    category = CategorySerializer(
        many=True,
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )


class PostImageSerializer(serializers.ModelSerializer):
    """
    Serializer class for downloading images to post model
    """
    class Meta:
        model = Post
        fields = ('slug', 'image')
        read_only_fields = ('slug',)
        

