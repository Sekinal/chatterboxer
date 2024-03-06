import sys
from pathlib import Path
import markdown
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                  QTextEdit, QLineEdit, QPushButton)
import polars as pl

class ChatWindow(QMainWindow):
    """
    Represents the main chat interface of the ChatterBoxer application.
    """
    
    def __init__(self):
        """
        Initializes the chat window, sets up UI elements, and loads conversation data.
        """
        super().__init__()
        self.setWindowTitle("ChatterBoxer")
        self.conversation = [{"from": "system", "value": ""}]
        self.save_dir = Path("save_data")  # Create a Path object
        self.save_dir.mkdir(parents=True, exist_ok=True)  # Create if necessary
        self.conv_id = self.initialize_conv_id()  # Initialize conv_id here

        # UI Elements
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.user_input = QLineEdit()
        self.ai_input = QLineEdit()
        self.add_user_button = QPushButton("Add User Response")
        self.add_ai_button = QPushButton("Add Assistant Response")
        self.new_conversation_button = QPushButton("Save Conversation (and create a new one))")
        self.save_all_button = QPushButton("Save All Conversations (USE ONLY AFTER SAVING)")
        
        # Layout (Example)
        layout = QVBoxLayout()
        layout.addWidget(self.conversation_display)
        layout.addWidget(self.user_input)
        layout.addWidget(self.add_user_button)
        layout.addWidget(self.ai_input)
        layout.addWidget(self.add_ai_button)
        layout.addWidget(self.new_conversation_button)
        layout.addWidget(self.save_all_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect buttons to functions
        self.add_user_button.clicked.connect(self.add_user_response)
        self.add_ai_button.clicked.connect(self.add_assistant_response)
        self.new_conversation_button.clicked.connect(self.new_conversation)
        self.save_all_button.clicked.connect(self.save_all)

    def initialize_conv_id(self) -> int:
        """
        Determines the next available conversation ID.

        Returns:
            int: The next available conversation ID.
        """
        conversation_files = [f for f in (self.save_dir/"individual_conversations").iterdir() if f.suffix == ".parquet"] 

        if conversation_files:
            highest_num = max(
                int(f.stem.split("_")[1]) for f in conversation_files  # Use .stem
            )
            return highest_num + 1
        else:
            return 0
    
    def add_user_response(self, user_message: str) -> None:
        """
        Adds a user message to the conversation history and updates the display.

        Args:
            user_message (str): The message entered by the user.
        """
        user_message = self.user_input.text()
        response_dict = {
            "from": "human",
            "value": user_message
        }
        print(self.conv_id)
        self.conversation.append(response_dict)
        self.update_conversation_display()
        self.user_input.clear()

    def add_assistant_response(self) -> None:
        """
        Adds an assistant message to the conversation history and updates the display.

        Args:
            user_message (str): The message entered by the assistant.
        """
        assistant_message = self.ai_input.text()
        response_dict = {
            "from": "gpt",
            "value": assistant_message
        }
        self.conversation.append(response_dict)
        self.update_conversation_display()
        self.ai_input.clear()

    def update_conversation_display(self) -> None:
        self.conversation_display.clear()
        for message in self.conversation:
                html_message = markdown.markdown(message["value"], extensions=['extra', 'codehilite']) 

                # Expanded CSS styles
                with open("chatterboxer/style/chat_style.css", 'r') as chat_style:
                    style = chat_style.read()

                html_message = f"<style>{style}</style>{html_message}"
                self.conversation_display.append(f"{message['from']}: {html_message}")

    def save_conversation(self) -> None:
        convo_df = pl.DataFrame({"conversation": [self.conversation]})
        
        save_file = self.save_dir / f"individual_conversations/conversation_{self.conv_id}.parquet"
        convo_df.write_parquet(save_file)
        self.conv_id += 1
    
    def new_conversation(self) -> None:
        self.save_conversation()
        self.conversation = [{"from": "system", "value": ""}]
        self.conversation_display.clear()
    
    def save_all(self) -> None:
        """Saves all conversation data to a file."""
        convo_df = pl.DataFrame()
        for conversation_file in (self.save_dir/"individual_conversations").iterdir():
            if conversation_file.suffix == '.parquet': 
                convo_tmp_df = pl.read_parquet(conversation_file)
                convo_df = pl.concat([convo_df, convo_tmp_df])

        convo_df = convo_df.rename({"conversation":"conversations"})
        save_file = self.save_dir / "conversations/conversations.parquet"
        convo_df.write_parquet(save_file)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    with open("chatterboxer/style/style.qss", 'r') as chat_style:
        app.setStyleSheet(chat_style.read())
    
    window = ChatWindow()

    window.show()
    sys.exit(app.exec()) 