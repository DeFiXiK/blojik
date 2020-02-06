from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property


class PublicationManager(models.Manager):

    def get_all_published_news(self):
        return self.get_queryset().filter(
            publication_type=Publication.PUBLICATION_TYPE_NEWS,
            published_at__lte=timezone.now())

    def get_all_published_articles(self):
        return self.get_queryset().filter(
            publication_type=Publication.PUBLICATION_TYPE_ARTICLE,
            published_at__lte=timezone.now())


class Publication(models.Model):
    PUBLICATION_TYPE_NEWS = 'news'
    PUBLICATION_TYPE_ARTICLE = 'article'

    PUBLICATION_TYPE_CHOICES = [
        (PUBLICATION_TYPE_NEWS, 'news'),
        (PUBLICATION_TYPE_ARTICLE, 'article'),
    ]

    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField()
    author = models.CharField(max_length=255)
    publication_type = models.CharField(choices=PUBLICATION_TYPE_CHOICES,
                                        default=PUBLICATION_TYPE_NEWS,
                                        max_length=7)

    objects = PublicationManager()

    @cached_property
    def votes_count(self):
        return self.votes_set.count()

    @cached_property
    def votes_up_count(self):
        return self.votes_set.filter(is_up=True).count()

    @cached_property
    def votes_down_count(self):
        return self.votes_set.filter(is_up=False).count()

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE,
                                    related_name='comments_set')
    text = models.TextField()

    @cached_property
    def votes_count(self):
        return self.votes_set.count()

    @cached_property
    def votes_up_count(self):
        return self.votes_set.filter(is_up=True).count()

    @cached_property
    def votes_down_count(self):
        return self.votes_set.filter(is_up=False).count()


class Vote(models.Model):
    is_up = models.BooleanField()

    class Meta:
        abstract = True


class VoteComment(Vote):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE,
                                related_name="votes_set")


class VotePublication(Vote):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE,
                                    related_name="votes_set")
