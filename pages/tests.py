from datetime import timedelta

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Publication, Comment, VoteComment, VotePublication


class PublicationIndexViewTest(TestCase):

    def setUp(self):
        for i in range(45):
            Publication.objects.create(
                title=f"Новость {i}",
                text="ЛоРЕМ ИПСУМ",
                author="Олег",
                published_at=timezone.now() - timedelta(hours=2),
            )

        Publication.objects.create(
            title=f"Публикация {323}",
            text="ЛоРЕМ ИПСУМ",
            author="Олег",
            published_at=timezone.now() + timedelta(hours=2),
        )

        for i in range(40):
            Publication.objects.create(
                title=f"Статья {i + 45}",
                text="ЛоРЕМ ИПСУМ",
                author="Олег",
                published_at=timezone.now() - timedelta(hours=2),
                publication_type=Publication.PUBLICATION_TYPE_ARTICLE
            )

    def test_index_page(self):
        response = self.client.get(reverse("pages:publications-index-view"))
        self.assertEqual(len(response.context['news'].object_list), 10)
        self.assertEqual(len(response.context['articles'].object_list), 10)

    def test_paginate_index_page(self):
        response = self.client.get(
            reverse("pages:publications-index-view") + "?news_page_number=5")
        self.assertEqual(len(response.context['news'].object_list), 5)
        self.assertEqual(len(response.context['articles'].object_list), 10)

        response = self.client.get(
            reverse(
                "pages:publications-index-view") + "?articles_page_number=6")

        self.assertEqual(len(response.context['news']), 10)
        self.assertEqual(len(response.context['articles']), 0)


class PublicationViewTest(TestCase):
    def setUp(self):
        Publication.objects.create(
            title="Новость 1",
            text="ЛоРЕМ ИПСУМ",
            author="Олег",
            published_at=timezone.now() - timedelta(hours=2),
        )

    def test_showing_page(self):
        response = self.client.get(
            reverse("pages:publication-detail-view", kwargs={'pk': 1}))
        self.assertEqual(response.context['object'].title, "Новость 1")

    def test_bad_page(self):
        response = self.client.get(
            reverse("pages:publication-detail-view", kwargs={'pk': 22}))
        self.assertEqual(response.status_code, 404)


class CommentCreationViewTest(TestCase):

    def setUp(self):
        Publication.objects.create(
            title="Новость 1",
            text="ЛоРЕМ ИПСУМ",
            author="Олег",
            published_at=timezone.now() - timedelta(hours=2),
        )

    def test_right_creation(self):
        response = self.client.post(reverse("pages:create-comment-view"), {
            'publication': 1,
            'text': "Лорем лорем"
        })

        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertEqual(resp_json['status'], 'success')

        p = Publication.objects.first()
        self.assertEqual(p.comments_set.all().first().text, "Лорем лорем")

    def test_bad_creation(self):
        response = self.client.post(reverse("pages:create-comment-view"), {
            'text': "Лорем лорем"
        }).json()

        self.assertEqual(response['status'], 'error')

        response = self.client.post(reverse("pages:create-comment-view"), {
            'publication': 1,
        }).json()

        self.assertEqual(response['status'], 'error')


class VoteViewTest(TestCase):

    def setUp(self):
        publication = Publication.objects.create(
            title="Новость 1",
            text="ЛоРЕМ ИПСУМ",
            author="Олег",
            published_at=timezone.now() - timedelta(hours=2),
        )

        Comment.objects.create(
            publication=publication,
            text="Лорем ипсум"
        )

    def test_right_vote(self):
        response = self.client.post(reverse("pages:vote"), {
            'vote_type': True,
            'obj_type': 'publication',
            'obj_id': 1,
        })

        resp_json = response.json()
        self.assertEqual(resp_json['status'], 'success')

        vote = VotePublication.objects.get(id=1)
        self.assertEqual(vote.publication.id, 1)
        self.assertTrue(vote.is_up)
        self.assertEqual(vote.publication.text, "ЛоРЕМ ИПСУМ")

        response = self.client.post(reverse("pages:vote"), {
            'vote_type': False,
            'obj_type': 'comment',
            'obj_id': 1,
        })

        resp_json = response.json()
        self.assertEqual(resp_json['status'], 'success')
        vote = VoteComment.objects.get(id=1)
        self.assertEqual(vote.comment.id, 1)
        self.assertFalse(vote.is_up)
        self.assertEqual(vote.comment.text, "Лорем ипсум")

    def test_bad_creation(self):
        response = self.client.post(reverse("pages:vote"), {
            'vote_type': True,
            'obj_type': 'publication',
        })

        resp_json = response.json()
        self.assertEqual(resp_json['status'], 'error')

        response = self.client.post(reverse("pages:vote"), {
            'vote_type': True,
            'obj_id': 1,
        })

        resp_json = response.json()
        self.assertEqual(resp_json['status'], 'error')

        response = self.client.post(reverse("pages:vote"), {
            'vote_type': True,
        })

        resp_json = response.json()
        self.assertEqual(resp_json['status'], 'error')


class VotesCountTest(TestCase):
    def setUp(self):
        self.publication = Publication.objects.create(
            title="Новость 1",
            text="ЛоРЕМ ИПСУМ",
            author="Олег",
            published_at=timezone.now() - timedelta(hours=2),
        )

        self.comment = Comment.objects.create(
            publication=self.publication,
            text="Лорем ипсум"
        )

        for i in range(10):
            VoteComment.objects.create(
                comment=self.comment,
                is_up=True
            )

        for i in range(10):
            VoteComment.objects.create(
                comment=self.comment,
                is_up=False
            )

        for i in range(15):
            VotePublication.objects.create(
                publication=self.publication,
                is_up=True
            )

        for i in range(20):
            VotePublication.objects.create(
                publication=self.publication,
                is_up=False
            )

    def counter_validation(self):
        self.assertEqual(self.publication.votes_count, 35)
        self.assertEqual(self.publication.votes_up_count, 15)
        self.assertEqual(self.publication.votes_down_count, 20)

        self.assertEqual(self.comment.votes_count, 20)
        self.assertEqual(self.comment.votes_up_count, 10)
        self.assertEqual(self.comment.votes_down_count, 10)
