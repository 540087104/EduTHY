"""AIQandA 应用的 URL 路由。"""

from django.urls import path

from . import views

app_name = "AIQandA"

urlpatterns = [
    path("", views.index, name="index"),
    path("ask/", views.ask, name="ask"),
]
