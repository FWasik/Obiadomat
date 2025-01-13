from django.urls import path
from . import views


app_name = "lunch_sessions"

urlpatterns = [
    path("", views.LunchSessionListView.as_view(), name="lunch_session_list"),
    path(
        "create/", views.LunchSessionCreateView.as_view(), name="lunch_session_create"
    ),
    path(
        "update/<int:pk>/",
        views.LunchSessionUpdateView.as_view(),
        name="lunch_session_update",
    ),
    path(
        "delete/<int:pk>/",
        views.LunchSessionDeleteView.as_view(),
        name="lunch_session_delete",
    ),
    path(
        "<int:pk>/",
        views.LunchSessionWithOrderDetailView.as_view(),
        name="lunch_session_with_order",
    ),
    path(
        "<int:pk>/orders/",
        views.LunchSessionOrdersListView.as_view(),
        name="lunch_session_orders",
    ),
    path(
        "<int:session_id>/order/create/", views.create_order_view, name="order_create"
    ),
    path(
        "<int:session_id>/order/update/<int:order_id>/",
        views.OrderUpdateView.as_view(),
        name="order_update",
    ),
    path(
        "<int:session_id>/order/delete/<int:order_id>/",
        views.delete_order_view,
        name="order_delete",
    ),
    path(
        "raport/<int:pk>/",
        views.LunchSessionReportDetailView.as_view(),
        name="lunch_session_raport",
    ),
]
