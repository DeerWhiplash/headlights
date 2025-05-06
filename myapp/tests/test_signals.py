from django.conf import settings
from django.db import models, connection
from django.test import TransactionTestCase, override_settings

from unittest.mock import patch

from myapp.models import DatabaseLog, OperationLookup, TableLookup, User, UserProfile

class MockModel(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        app_label = 'myapp'

@override_settings(INSTALLED_APPS=['myapp'])
class LoggingSignalsTest(TransactionTestCase):
    reset_sequences = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(MockModel)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(MockModel)
        super().tearDownClass()

    def setUp(self):
        self.user, _ = User.objects.get_or_create(username="test_user")
        self.user_profile, _ = UserProfile.objects.get_or_create(auth_id=self.user)

        self.operation_create, _ = OperationLookup.objects.get_or_create(pk=1, operation_name="CREATE")
        self.operation_update, _ = OperationLookup.objects.get_or_create(pk=3, operation_name="UPDATE")
        self.operation_delete, _ = OperationLookup.objects.get_or_create(pk=4, operation_name="DELETE")

        self.table_lookup, _ = TableLookup.objects.get_or_create(table_name='MockModel')

        settings.TESTING = False
        super().setUp()

    @override_settings(TESTING=False)
    @patch("myapp.middleware.get_current_user")
    def test_log_create_signal(self, mock_get_current_user):
        mock_get_current_user.return_value = self.user_profile.auth_id

        MockModel.objects.create(name="Test")

        self.assertTrue(DatabaseLog.objects.filter(
            affected_table_id=self.table_lookup,
            operation_performed=self.operation_create
        ).exists())
    
    @override_settings(TESTING=False)
    @patch("myapp.middleware.get_current_user")
    def test_log_update_signal(self, mock_get_current_user):
        mock_get_current_user.return_value = self.user_profile.auth_id

        instance = MockModel.objects.create(name="Test")
        instance.name = "Updated"
        instance.save()

        self.assertTrue(DatabaseLog.objects.filter(
            affected_table_id=self.table_lookup,
            operation_performed=self.operation_update
        ).exists())
    
    @override_settings(TESTING=False)
    @patch("myapp.middleware.get_current_user")
    def test_log_delete_signal(self, mock_get_current_user):
        mock_get_current_user.return_value = self.user_profile.auth_id

        instance = MockModel.objects.create(name="Test")
        instance.delete()

        self.assertTrue(DatabaseLog.objects.filter(
            affected_table_id=self.table_lookup,
            operation_performed=self.operation_delete
        ).exists())

    @override_settings(TESTING=False)
    @patch("myapp.middleware.get_current_user")
    def test_log_create_signal_without_user(self, mock_get_current_user):
        mock_get_current_user.return_value = None

        MockModel.objects.create(name="Test")

        self.assertTrue(DatabaseLog.objects.exists())
