"""URL для короткой ссылки на рецепт."""

from django.urls import path

from api.views import redirect_view

urlpatterns = [
    path('<slug:tiny>/', view=redirect_view, name='short_url_view')
]
