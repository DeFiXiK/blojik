from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import generic
from django.http import JsonResponse

from .models import Publication
from .forms import CommentForm, VoteForm


class PublicationIndexView(generic.View):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        context = {}

        news = Paginator(
            Publication.objects.get_all_published_news(), 10)
        articles = Paginator(
            Publication.objects.get_all_published_articles(), 10)

        news_page_number = self.request.GET.get('news_page_number', 1)
        articles_page_number = self.request.GET.get('articles_page_number', 1)

        if int(news_page_number) > news.num_pages:
            context['news'] = []
        else:
            context['news'] = news.get_page(news_page_number)
        if int(articles_page_number) > articles.num_pages:
            context['articles'] = []
        else:
            context['articles'] = articles.get_page(articles_page_number)

        return context

    def get(self, request):
        return render(request, self.template_name, self.get_context_data())


class PublicationDetailView(generic.DetailView):
    template_name = 'pages/detail.html'
    model = Publication


class CommentCreationAjaxView(generic.View):
    def post(self, request):
        form = CommentForm(request.POST)
        if not form.is_valid():
            return JsonResponse({
                'status': 'error',
                'message': form.errors
            })

        form.save()
        return JsonResponse({
            'status': 'success',
            'message': 'ok',
        })


class VoteAjaxView(generic.View):
    def post(self, request):
        form = VoteForm(request.POST)
        if not form.is_valid():
            return JsonResponse({
                'status': 'error',
                'message': form.errors
            })

        form.save()
        return JsonResponse({
            'status': 'success',
            'message': 'ok'
        })

