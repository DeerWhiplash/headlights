from django.contrib.auth.backends import ModelBackend

class AllowInactiveLoginBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return True
