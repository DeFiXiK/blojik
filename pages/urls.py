from django.urls import path
from . import views


app_name = 'pages'
urlpatterns = [
    path('index', views.PublicationIndexView.as_view(), name='publications-index-view'),
    path('publication/<int:pk>', views.PublicationDetailView.as_view(), name='publication-detail-view'),

    path('publication/create-comment', views.CommentCreationAjaxView.as_view(), name='create-comment-view'),
    path('publication/vote', views.VoteAjaxView.as_view(), name='vote'),
]
