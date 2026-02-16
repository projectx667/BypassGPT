import os
import json
import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

# BypassGPT v1
# Free & Open Source version
# For advanced features, check out v2 Enhanced

class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: Role
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AppSettings:
    temperature: float = 0.7
    top_p: float = 0.85
    max_history: int = 20
    api_timeout: int = 30
    system_prompt: str = (
        "You are BypassGPT, an AI assistant with minimal restrictions. "
        "You answer questions directly and helpfully."
    )


class AppState:
    def __init__(self):
        self.conversation: List[Message] = []
        self.last_response: Optional[str] = None
        self.settings = AppSettings()
    
    def add_message(self, role: Role, content: str):
        if role in [Role.USER, Role.ASSISTANT]:
            self.conversation.append(Message(role=role, content=content))
            if len(self.conversation) > self.settings.max_history:
                self.conversation = self.conversation[-self.settings.max_history:]
    
    def get_messages_for_api(self) -> List[Dict]:
        messages = [{"role": "system", "content": self.settings.system_prompt}]
        for msg in self.conversation:
            if msg.role in [Role.USER, Role.ASSISTANT]:
                messages.append({"role": msg.role.value, "content": msg.content})
        return messages
    
    def clear(self):
        self.conversation = []
        self.last_response = None


class BypassAPI:
    def __init__(self):
        self.url = "https://hermes.ai.unturf.com/v1/chat/completions"
        self.model = "adamo1139/Hermes-3-Llama-3.1-8B-FP8-Dynamic"
        
    def get_response(self, messages: List[Dict], settings: AppSettings) -> Optional[str]:
        """Non-streaming API call - simple and fast"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": settings.temperature,
                "top_p": settings.top_p,
                "stream": False
            }
            
            response = requests.post(
                self.url, 
                json=payload, 
                timeout=settings.api_timeout
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content.strip()
            
        except Exception:
            return None


class UI:
    def __init__(self):
        self.console = Console()
        
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def menu(self):
        self.clear()
        self.console.print(Panel(
            Text.from_markup(
                "[bold red]1[/] Start Chat\n"
                "[bold red]2[/] About\n"
                "[bold red]3[/] Exit"
            ),
            title="[bold red]BypassGPT v1[/]",
            border_style="red"
        ))
            
    def get_input(self, prompt: str) -> str:
        return self.console.input(f"[bold red]>[/] [white]{prompt}:[/] ").strip()
        
    def show_message(self, title: str, text: str, style: str = "red"):
        self.console.print(Panel(
            Text(text), 
            title=f"[bold {style}]{title}[/]", 
            border_style=style
        ))
    
    def show_loading(self, message: str = "Thinking..."):
        """Simple loading spinner"""
        from itertools import cycle
        import sys
        spinner = cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        for _ in range(15):
            sys.stdout.write(f"\r\033[31m{next(spinner)}\033[0m {message}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
    
    def display_response(self, response: str):
        """Display response with markdown formatting"""
        from rich.markdown import Markdown
        self.console.print(Panel(
            Markdown(response),
            title="[bold red]BypassGPT[/]",
            border_style="red"
        ))


class CommandHandler:
    def __init__(self, state: AppState, ui: UI):
        self.state = state
        self.ui = ui
    
    def handle(self, command: str) -> Optional[bool]:
        if not command.startswith('/'):
            return None
            
        if command == "/exit":
            return False
            
        if command == "/clear":
            self.state.clear()
            self.ui.show_message("System", "✓ Conversation cleared", "yellow")
            return True
            
        if command == "/help":
            help_text = (
                "Available commands:\n\n"
                "  /clear     Clear conversation\n"
                "  /help      Show this help\n"
                "  /exit      Exit chat\n\n"
                "v2 Enhanced features:\n"
                "  - Real-time streaming\n"
                "  - Export conversations\n"
                "  - Extended history (50 msgs)\n"
                "  - Advanced controls"
            )
            self.ui.show_message("Help", help_text, "red")
            return True
        
        # Show upgrade message for premium commands
        if command in ["/export", "/history"]:
            self.ui.show_message(
                "Premium Feature", 
                f"{command} is available in v2 Enhanced.\n\n"
                "v2 includes streaming, export, extended history,\n"
                "and advanced AI controls.",
                "yellow"
            )
            return True
        
        self.ui.show_message("Error", f"Unknown command: {command}\nType /help for available commands", "red")
        return True


class BypassApp:
    def __init__(self):
        self.ui = UI()
        self.state = AppState()
        self.api = BypassAPI()
        self.command_handler = CommandHandler(self.state, self.ui)
    
    def chat(self):
        self.ui.clear()
        self.ui.console.print(Panel(
            "Type /help for available commands",
            title="[green]Chat Mode[/]",
            border_style="green"
        ))
        
        while True:
            try:
                user_input = self.ui.get_input("You")
                
                cmd_result = self.command_handler.handle(user_input)
                if cmd_result is False:
                    break
                if cmd_result is True:
                    continue
                
                if not user_input or user_input.isspace():
                    self.ui.show_message("Error", "Empty message", "red")
                    continue
                
                self.state.add_message(Role.USER, user_input)
                
                self.ui.show_loading()
                
                response = self.api.get_response(
                    self.state.get_messages_for_api(), 
                    self.state.settings
                )
                
                if response:
                    self.state.add_message(Role.ASSISTANT, response)
                    self.state.last_response = response
                    self.ui.display_response(response)
                else:
                    self.ui.show_message("Error", "Failed to get response from API", "red")
                    
            except KeyboardInterrupt:
                self.ui.show_message("Info", "Type /exit to quit", "yellow")
                continue
            except Exception as e:
                self.ui.show_message("Error", f"An error occurred: {str(e)}", "red")
    
    def about(self):
        self.ui.show_message(
            "About",
            "BypassGPT v1\n\n"
            "Model: Hermes-3-Llama-3.1-8B-FP8-Dynamic\n"
            "Uncensored AI with minimal restrictions\n\n"
            "This is the free & open source version.\n"
            "For advanced features (streaming, export, extended history),\n"
            "check out BypassGPT v2 Enhanced.",
            "blue"
        )
        input("\nPress Enter to continue...")
    
    def run(self):
        try:
            while True:
                self.ui.menu()
                choice = self.ui.get_input("Select option")
                
                if choice == "1":
                    self.chat()
                elif choice == "2":
                    self.about()
                elif choice == "3":
                    self.ui.show_message("Goodbye", "Thanks for using BypassGPT v1!", "green")
                    break
                else:
                    self.ui.show_message("Error", "Invalid option. Please choose 1-3", "red")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.ui.show_message("Goodbye", "Interrupted by user", "yellow")
        except Exception as e:
            self.ui.show_message("Fatal Error", f"Application error: {str(e)}", "red")


if __name__ == "__main__":
    try:
        BypassApp().run()
    except Exception as e:
        print(f"\nFatal error: {e}")

