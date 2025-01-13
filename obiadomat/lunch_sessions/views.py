from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.views.generic import ListView
from .models import LunchSession, Order
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import LunchSessionForm
from django.utils import timezone
from django.contrib.auth import get_user_model
from .mixins import (
    CustomSessionDeleteTestMixin,
    CustomSessionUpdateTestMixin,
    CustomSessionWithOrdersTestMixin,
    CustomSessionWithRaportTestMixin,
    CustomSessionWithOrderTestMixin,
    CustomOrderTestMixin,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import LunchSession, Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from django.contrib import messages
from django.db import IntegrityError
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .decorators import (
    creator_or_owner_required,
    creator_or_participation_required,
    time_check_required,
)
import obiadomat.settings as settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Sum, F, DecimalField
from django.views import View

User = get_user_model()


class LunchSessionCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = LunchSession
    form_class = LunchSessionForm
    template_name = "lunch_session_form.html"
    success_url = reverse_lazy("lunch_sessions:lunch_session_list")
    success_message = "You successfully created a lunch session!"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)

        self.send_invites(form.instance)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.get("form").fields["participants"].queryset = User.objects.exclude(
            id=self.request.user.id
        )

        return context

    def send_invites(self, session):
        session_url = f"{settings.HOST}{reverse_lazy('lunch_sessions:lunch_session_with_order', kwargs={'pk': session.pk})}"

        subject = "Invitation to Join Lunch Session"
        template_name = "emails/lunch_session_invitation.html"
        context = {
            "session": session,
            "session_url": session_url,
        }
        recipients = [participant.email for participant in session.participants.all()]

        custom_send_email(subject, template_name, context, recipients)


class LunchSessionListView(LoginRequiredMixin, ListView):
    model = LunchSession
    template_name = "lunch_session_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_time = timezone.localtime(timezone.now())

        pending_created_sessions = user.created_sessions.filter(
            edit_time__gte=current_time
        ).exclude(orders__orderer=user)
        pending_assigned_sessions = user.participated_sessions.filter(
            edit_time__gte=current_time
        ).exclude(orders__orderer=user)

        active_created_sessions = user.created_sessions.filter(
            edit_time__gte=current_time, orders__orderer=user
        )
        active_assigned_sessions = user.participated_sessions.filter(
            edit_time__gte=current_time, orders__orderer=user
        )

        inactive_created_sessions = user.created_sessions.filter(
            delivery_time__gte=current_time, edit_time__lt=current_time
        )
        inactive_assigned_sessions = user.participated_sessions.filter(
            delivery_time__gte=current_time, edit_time__lt=current_time
        )

        history_created_sessions = user.created_sessions.filter(
            delivery_time__lt=current_time
        )
        history_assigned_sessions = user.participated_sessions.filter(
            delivery_time__lt=current_time
        )

        # pending_assigned_sessions = LunchSession.objects.filter(
        #     participants=user, edit_time__gte=current_time
        # ).exclude(orders__orderer=user)

        # pending_created_sessions = LunchSession.objects.filter(
        #     creator=user, edit_time__gte=current_time
        # ).exclude(orders__orderer=user)

        # active_created_sessions = LunchSession.objects.filter(
        #     creator=user, edit_time__gte=current_time
        # ).filter(orders__orderer=user)

        # active_assigned_sessions = LunchSession.objects.filter(
        #     participants=user, edit_time__gte=current_time
        # ).filter(orders__orderer=user)

        # inactive_created_sessions = LunchSession.objects.filter(
        #     creator=user, delivery_time__gte=current_time, edit_time__lt=current_time
        # )

        # inactive_assigned_sessions = LunchSession.objects.filter(
        #     participants=user,
        #     delivery_time__gte=current_time,
        #     edit_time__lt=current_time,
        # )

        # history_created_sessions = LunchSession.objects.filter(
        #     creator=user, delivery_time__lt=current_time
        # )

        # history_assigned_sessions = LunchSession.objects.filter(
        #     participants=user, delivery_time__lt=current_time
        # )

        # total_spent = (
        #     Order.objects.filter(orderer=user)
        #     .prefetch_related("order_items__meal")
        #     .aggregate(
        #         total_spent=Sum(
        #             F("order_items__meal__price") * F("order_items__portion"),
        #             output_field=DecimalField(),
        #         )
        #     )["total_spent"]
        #     or 0
        # )
        
        aggregated_meals = aggregate_meals(user.user_orders.all())
        total_spent = sum(
            item["total_meal_cost"] for item in aggregated_meals.values()
        )
        

        context.update(
            {
                "active_created_sessions": active_created_sessions,
                "active_assigned_sessions": active_assigned_sessions,
                "inactive_created_sessions": inactive_created_sessions,
                "inactive_assigned_sessions": inactive_assigned_sessions,
                "pending_assigned_sessions": pending_assigned_sessions,
                "pending_created_sessions": pending_created_sessions,
                "history_created_sessions": history_created_sessions,
                "history_assigned_sessions": history_assigned_sessions,
                "total_spent": total_spent,
            }
        )

        return context


class LunchSessionUpdateView(
    SuccessMessageMixin, CustomSessionUpdateTestMixin, LoginRequiredMixin, UpdateView
):
    model = LunchSession
    form_class = LunchSessionForm
    template_name = "lunch_session_form.html"
    success_url = reverse_lazy("lunch_sessions:lunch_session_list")
    success_message = "You successfully updated a lunch session!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.get("form").fields["participants"].queryset = User.objects.exclude(
            id=self.request.user.id
        )

        return context

    def form_valid(self, form):
        old_name = form.initial.get("name", None)
        response = super().form_valid(form)

        if form.has_changed():
            if "participants" in form.changed_data:
                form.changed_data.remove("participants")

            changes = get_form_changes(form)

            if changes:
                self.send_update_notification(form.instance, changes, old_name)

        return response

    def send_update_notification(self, session, changes, old_name=None):
        session_url = f"{settings.HOST}{reverse_lazy('lunch_sessions:lunch_session_with_order', kwargs={'pk': session.pk})}"

        subject = "Lunch Session Updated"
        template_name = "emails/lunch_session_update_notification.html"
        context = {
            "session": session,
            "session_url": session_url,
            "changes": changes,
            "old_name": old_name,
        }
        recipients = [participant.email for participant in session.participants.all()]

        custom_send_email(subject, template_name, context, recipients)


class LunchSessionDeleteView(
    SuccessMessageMixin,
    CustomSessionDeleteTestMixin,
    LoginRequiredMixin,
    DeleteView,
):
    model = LunchSession
    template_name = "lunch_session_confirm_delete.html"
    success_url = reverse_lazy("lunch_sessions:lunch_session_list")
    success_message = "You successfully deleted a lunch session!"


class LunchSessionWithOrderDetailView(
    LoginRequiredMixin, CustomSessionWithOrderTestMixin, DetailView
):
    model = LunchSession
    template_name = "lunch_session_with_order.html"
    context_object_name = "session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        user_order = session.orders.filter(orderer=self.request.user).first()

        aggregated_meals = aggregate_meals(session.orders.all())
        total_orders_value = sum(
            item["total_meal_cost"] for item in aggregated_meals.values()
        )

        user_total_cost = Decimal(0)

        if user_order:
            user_total_cost = sum(
                item.meal.price * item.portion for item in user_order.order_items.all()
            )

        order_form = OrderForm(instance=user_order)
        order_item_formset = OrderItemFormSet(
            instance=user_order, form_kwargs={"session": session}
        )

        context.update(
            {
                "order_form": order_form,
                "order_item_formset": order_item_formset,
                "user_order": user_order,
                "aggregated_meals": aggregated_meals,
                "total_orders_value": total_orders_value,
                "user_total_cost": user_total_cost,
            }
        )

        return context


class LunchSessionReportDetailView(
    LoginRequiredMixin, CustomSessionWithRaportTestMixin, DetailView
):
    model = LunchSession
    template_name = "lunch_session_raport.html"
    context_object_name = "session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        restaurant = session.restaurant
        orders = session.orders.all()
        
        # orders = Order.objects.filter(lunch_session=session)

        orders_with_costs = []
        for order in orders:
            total_cost = sum(
                item.meal.price * item.portion for item in order.order_items.all()
            )
            orders_with_costs.append(
                {
                    "order": order,
                    "total_cost": total_cost,
                }
            )

        aggregated_meals = aggregate_meals(orders)
        total_value = sum(item["total_meal_cost"] for item in aggregated_meals.values())

        context.update(
            {
                "restaurant": restaurant,
                "orders_with_costs": orders_with_costs,
                "aggregated_meals": aggregated_meals,
                "total_value": total_value,
            }
        )

        return context


class LunchSessionOrdersListView(
    LoginRequiredMixin, CustomSessionWithOrdersTestMixin, ListView
):
    model = Order
    template_name = "lunch_session_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        lunch_session = get_object_or_404(LunchSession, pk=self.kwargs.get("pk"))

        return lunch_session.orders.exclude(
            orderer=lunch_session.creator
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["session"] = get_object_or_404(LunchSession, pk=self.kwargs.get("pk"))

        return context


@login_required
@time_check_required
@creator_or_participation_required
def create_order_view(request, session_id):
    session = get_object_or_404(LunchSession, pk=session_id)

    try:
        Order.objects.create(lunch_session=session, orderer=request.user)
        
        messages.success(request, "You successfully created order!")

    except IntegrityError:
        messages.error(
            request, "There is already an order assigned by you to that session!"
        )

    return redirect("lunch_sessions:lunch_session_with_order", pk=session_id)


class OrderUpdateView(LoginRequiredMixin, CustomOrderTestMixin, View):
    def get_order_and_session(self, session_id, order_id):
        order = get_object_or_404(Order, pk=order_id)
        session = get_object_or_404(LunchSession, pk=session_id)

        return order, session

    def handle_email_notification(self, session, order_form, order_item_formset, order):
        form_changes = get_form_changes(order_form)
        formset_changes = get_formset_changes(order_item_formset)

        if form_changes or formset_changes:
            formset_items = [
                {
                    "meal": form.cleaned_data.get("meal"),
                    "portion": form.cleaned_data.get("portion"),
                }
                for form in order_item_formset
                if not form.cleaned_data.get("DELETE", False)
            ]

            deleted_items = [form.instance for form in order_item_formset.deleted_forms]

            subject = "Order Update for Lunch Session"
            template_name = "emails/order_update_notification.html"
            session_url = f"{settings.HOST}{reverse_lazy('lunch_sessions:lunch_session_with_order', kwargs={'pk': session.pk})}"

            context = {
                "session": session,
                "session_url": session_url,
                "form_changes": form_changes,
                "formset_items": formset_items,
                "deleted_items": deleted_items,
            }

            custom_send_email(subject, template_name, context, [order.orderer.email])

    def post(self, request, session_id, order_id):
        order, session = self.get_order_and_session(session_id, order_id)
        user = request.user

        is_creator_and_not_orderer = user == session.creator and user != order.orderer

        order_form = OrderForm(request.POST, instance=order)
        order_item_formset = OrderItemFormSet(request.POST, instance=order)

        if order_form.is_valid() and order_item_formset.is_valid():
            order_form.save()
            order_item_formset.save()

            messages.success(request, "You successfully updated the order!")

            if is_creator_and_not_orderer:
                self.handle_email_notification(
                    session, order_form, order_item_formset, order
                )

                return redirect("lunch_sessions:lunch_session_orders", pk=session_id)

            return redirect("lunch_sessions:lunch_session_with_order", pk=session_id)

        if is_creator_and_not_orderer:
            return self.render_update_form(request, order_form, order_item_formset)
        else:
            return redirect("lunch_sessions:lunch_session_with_order", pk=session_id)

    def render_update_form(self, request, order_form, order_item_formset):

        return render(
            request,
            "lunch_session_update_order.html",
            {
                "order_form": order_form,
                "order_item_formset": order_item_formset,
            },
        )

    def get(self, request, session_id, order_id):
        order, session = self.get_order_and_session(session_id, order_id)
        user = request.user

        if user == session.creator and user != order.orderer:
            order_form = OrderForm(instance=order)
            order_item_formset = OrderItemFormSet(instance=order)

            return self.render_update_form(request, order_form, order_item_formset)

        return redirect("lunch_sessions:lunch_session_list")


@login_required
@time_check_required
@creator_or_owner_required
def delete_order_view(request, session_id, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id)

        order_owner = order.orderer
        session = get_object_or_404(LunchSession, pk=session_id)
        user = request.user

        order.delete()

        if user == session.creator and user != order_owner:
            subject = "Order Cancel for Lunch Session"
            template_name = "emails/order_delete_notification.html"
            context = {
                "session": session,
            }

            custom_send_email(subject, template_name, context, [order_owner.email])

        messages.success(request, "You successfully deleted order!")

    except Exception as e:
        messages.error(request, e.message)

    return redirect("lunch_sessions:lunch_session_list")


###########################################################################################


def custom_send_email(subject, template_name, context, recipients):
    if not recipients:
        return

    html_message = render_to_string(template_name, context)

    email = EmailMessage(
        subject,
        html_message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)


def aggregate_meals(orders):
    meal_aggregate = {}
    order_items = OrderItem.objects.filter(order__in=orders)
    
    for order_item in order_items:
        meal = order_item.meal
        
        if meal.name not in meal_aggregate:
            meal_aggregate[meal.name] = {"portion": 0, "total_meal_cost": 0}
            
        meal_aggregate[meal.name]["portion"] += order_item.portion
        meal_aggregate[meal.name]["total_meal_cost"] += (
            meal.price * order_item.portion
        )

    return meal_aggregate


def get_form_changes(form):
    return {field: form.cleaned_data.get(field) for field in form.changed_data}


def get_formset_changes(formset):
    changes = []
    for form in formset:
        form_changes = get_form_changes(form)
        if form_changes:
            changes.append(form_changes)

    return changes
