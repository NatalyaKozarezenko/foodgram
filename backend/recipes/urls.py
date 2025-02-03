"""Url адреса приложения recipes."""

from django.urls import path

from recipes.views import redirect_view

urlpatterns = [
    path('s/<int:id>/', view=redirect_view, name='short_url_view'),
]
