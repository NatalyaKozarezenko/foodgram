"""
Ниже приведены неявные URL.

api/recipes/download_shopping_cart
api/recipes/<pk>/shopping_cart
api/recipes/<pk>/favorite
api/users/reset_password
api/recipes/<pk>/shopping_cart
api/recipes/<pk>/get-link
api/recipes/download_shopping_cart
api/users/<id>/subscribe
api/users/subscriptions
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from recipes.views import RecipeDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/', include('urlshort.urls')),
    path(
        'recipes/<int:pk>/',
        RecipeDetailView.as_view(),
        name='recipes-detail'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
