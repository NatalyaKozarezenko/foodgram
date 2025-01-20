"""URL для короткой ссылки на рецепт."""

from api.views import redirect_view
from django.urls import path

urlpatterns = [
    path('<slug:tiny>/', view=redirect_view, name='short_url_view')
]
