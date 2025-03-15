from django.test import TestCase

from myapp.utility.SimpleResults import Message, SimpleResult, SimpleResultWithPayload

class TestSimpleResults(TestCase):
    def test_message_creation(self):
        info_message = Message(False, "Info Message")
        error_message = Message(True, "Error Message")
        
        self.assertFalse(info_message.is_error, "Info message was incorrectly set as error message")
        self.assertEqual(info_message.text, "Info Message")
        
        self.assertTrue(error_message.is_error, "Error message was not flagged as an error message")
        self.assertEqual(error_message.text, "Error Message")
        
        
    def test_adding_simple_messages(self):
        simple_result = SimpleResult()
        
        simple_result.add_info_message("Info")
        simple_result.add_error_message("Error")
        
        info_messages = simple_result.get_info_messages()
        error_messages = simple_result.get_error_messages()
        
        self.assertEqual(len(info_messages), 1)
        self.assertEqual(len(error_messages), 1)
        self.assertTrue(simple_result.success, "Result was incorrectly marked as unsuccessful")
        
        simple_result.add_error_message_and_mark_unsuccessful("Error 2")
        error_messages = simple_result.get_error_messages()
        
        self.assertEqual(len(info_messages), 1)
        self.assertEqual(len(error_messages), 2)
        self.assertFalse(simple_result.success, "Result was not marked unsuccessful")
        
        
    def test_adding_messages_from_results(self):
        simple_result = SimpleResult()
        
        simple_result_with_messages = SimpleResult()
        simple_result_with_messages.add_info_message("Info")
        simple_result_with_messages.add_error_message("Error")
        
        simple_result.add_messages_from_result(simple_result_with_messages)
        info_messages = simple_result.get_info_messages()
        error_messages = simple_result.get_error_messages()
        
        self.assertEqual(len(info_messages), 1)
        self.assertEqual(len(error_messages), 1)
        self.assertTrue(simple_result.success, "Result was incorrectly marked as unsuccessful")
        
        simple_result.add_messages_from_result_and_mark_unsuccessful_if_error_found(simple_result_with_messages)
        info_messages = simple_result.get_info_messages()
        error_messages = simple_result.get_error_messages()
        
        self.assertEqual(len(info_messages), 2)
        self.assertEqual(len(error_messages), 2)
        self.assertFalse(simple_result.success, "Result was not marked unsuccessful")
        
        
    def test_payload(self):
        simple_result_with_payload = SimpleResultWithPayload()
        simple_result_with_payload.payload = 1
        
        self.assertEqual(simple_result_with_payload.payload, 1)
        
        simple_result_with_payload.payload = "one"
        
        self.assertEqual(simple_result_with_payload.payload, "one")
        