class Message():
    
    def __init__(self, is_error: bool = False, text: str = ""):
        self.is_error = is_error
        self.text = text

class SimpleResult():
    def __init__(self):
        self.success: bool = True
        self.messages: list[Message] = []
    
    def add_info_message(self, text: str) -> None:
        self.messages.append(Message(False, text))
        
    def add_error_message(self, text: str) -> None:
        self.messages.append(Message(True, text))
        
    def add_error_message_and_mark_unsuccessful(self, text: str) -> None:
        self.messages.append(Message(True, text))
        self.success = False
        
    def add_messages_from_result(self, simple_result) -> None:
        self.messages += simple_result.messages
        
    def add_messages_from_result_and_mark_unsuccessful_if_error_found(self, simple_result) -> None:
        self.messages += simple_result.messages
        if len([message for message in simple_result.messages if message.is_error]) > 0:
            self.success = False
    
    def get_info_messages(self) -> list[Message]:
        return [message for message in self.messages if not message.is_error]
    
    def get_error_messages(self) -> list[Message]:
        return [message for message in self.messages if message.is_error]

class SimpleResultWithPayload(SimpleResult):
    def __init__(self):
        super().__init__()
        self.payload: any = None