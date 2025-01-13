from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone
from .models import LunchSession, Order
from django.shortcuts import get_object_or_404


class BaseSessionTestMixin(UserPassesTestMixin):
    def get_session(self, name_of_parameter):
        session_id = self.kwargs.get(name_of_parameter)
        return get_object_or_404(LunchSession, pk=session_id)

    def get_order(self):
        order_id = self.kwargs.get("order_id")
        return get_object_or_404(Order, pk=order_id)

    def is_creator(self, session, user):
        return user == session.creator

    def is_participant(self, session, user):
        return user in session.participants.all()

    def is_delivery_time_valid(self, session):
        return session.delivery_time >= timezone.localtime(timezone.now())

    def is_edit_time_valid(self, session):
        return session.edit_time >= timezone.localtime(timezone.now())

    def is_orderer(self, order, user):
        return user == order.orderer


class CustomSessionDeleteTestMixin(BaseSessionTestMixin):
    def test_func(self):
        session = self.get_object()

        return self.is_creator(session, self.request.user)


class CustomSessionUpdateTestMixin(BaseSessionTestMixin):
    def test_func(self):
        session = self.get_object()
        user = self.request.user

        return self.is_creator(session, user) and self.is_delivery_time_valid(session)


class CustomSessionWithOrderTestMixin(BaseSessionTestMixin):
    def test_func(self):
        session = self.get_object()
        user = self.request.user

        if not (self.is_creator(session, user) or self.is_participant(session, user)):
            return False

        if not self.is_creator(session, user) and not self.is_edit_time_valid(session):
            return False

        return self.is_delivery_time_valid(session)


class CustomSessionWithRaportTestMixin(BaseSessionTestMixin):
    def test_func(self):
        session = self.get_object()

        return self.is_creator(session, self.request.user)


class CustomSessionWithOrdersTestMixin(BaseSessionTestMixin):
    def test_func(self):
        session = self.get_session("pk")
        user = self.request.user

        return self.is_creator(session, user) and self.is_delivery_time_valid(session)


class CustomOrderTestMixin(BaseSessionTestMixin):
    def test_func(self):
        session = self.get_session("session_id")
        order = self.get_order()
        user = self.request.user

        if self.is_creator(session, user) and self.is_delivery_time_valid(session):
            return True

        return self.is_orderer(order, user) and self.is_edit_time_valid(session)
