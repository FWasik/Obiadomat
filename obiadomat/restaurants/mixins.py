from django.contrib.auth.mixins import UserPassesTestMixin


class CreatorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        restaurant = self.get_object()

        if self.request.user == restaurant.creator:
            return True

        return False
