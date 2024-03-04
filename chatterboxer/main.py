import sys
import os
import markdown
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                  QTextEdit, QLineEdit, QPushButton)
import polars as pl

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatterBoxer")
        self.conversation = [{"from": "system", "value": ""}]
        self.conv_id = 0

        # UI Elements
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.user_input = QLineEdit()
        self.ai_input = QLineEdit()
        self.add_user_button = QPushButton("Add User Response")
        self.add_ai_button = QPushButton("Add Assistant Response")
        self.new_conversation_button = QPushButton("Save Conversation (& create a new one))")
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

    def add_user_response(self):
        user_message = self.user_input.text()
        response_dict = {
            "from": "human",
            "value": user_message
        }
        self.conversation.append(response_dict)
        self.update_conversation_display()
        self.user_input.clear()

    def add_assistant_response(self):
        assistant_message = self.ai_input.text()
        response_dict = {
            "from": "gpt",
            "value": assistant_message
        }
        self.conversation.append(response_dict)
        self.update_conversation_display()
        self.ai_input.clear()

    def update_conversation_display(self):
        self.conversation_display.clear()
        for message in self.conversation:
                html_message = markdown.markdown(message["value"], extensions=['extra', 'codehilite']) 

                # Expanded CSS styles
                with open("chatterboxer/style/chat_style.css", 'r') as chat_style:
                    style = chat_style.read()

                html_message = f"<style>{style}</style>{html_message}"
                self.conversation_display.append(f"{message['from']}: {html_message}")

    def save_conversation(self):
        convo_df = pl.DataFrame({"conversation": [self.conversation]})
        convo_df.write_parquet(f"save_data/conversation/conversation_{self.conv_id}.parquet")
        self.conv_id += 1
    
    def new_conversation(self):
        self.save_conversation()
        self.conversation = [{"from": "system", "value": ""}]
        self.conversation_display.clear()
    
    def save_all(self):
        convo_df = pl.DataFrame()
        for conversation in os.listdir("save_data/conversation"):
            print(conversation)
            convo_tmp_df = pl.read_parquet(f"save_data/conversation/{conversation}")
            convo_df = pl.concat([convo_df, convo_tmp_df])
        
        convo_df.write_parquet(f"save_data/conversations/conversations.parquet")
        print(convo_df)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    with open("chatterboxer/style/style.qss", 'r') as chat_style:
        app.setStyleSheet(chat_style.read())
    
    window = ChatWindow()

    window.show()
    sys.exit(app.exec()) 