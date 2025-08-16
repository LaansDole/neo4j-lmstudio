#!/usr/bin/env python3
"""
LM Studio Tool Use Demo: Wikipedia Querying Chatbot (Official SDK)
Demonstrates how an LM Studio model can query Wikipedia using the official SDK
This example is updated to use the official LMStudio Python SDK instead of OpenAI-compatible API.
"""

# Standard library imports
import os
import itertools
import json
import shutil
import sys
import threading
import time
import urllib.parse
import urllib.request

# Official LMStudio SDK import
import lmstudio as lms
from dotenv import load_dotenv

# Add src to path for our package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from neo4j_lmstudio.core.client import LMStudioClient

# Load environment variables
load_dotenv()

# Configure the LM Studio client using official SDK
LMS_HOST = os.getenv("LMSTUDIO_API_HOST", "localhost:1234")
MODEL = os.getenv("LMSTUDIO_CHAT_MODEL", "openai/gpt-oss-20b")

# Configure default client
lms.configure_default_client(LMS_HOST)

# Get our enhanced client
client = LMStudioClient(server_host=LMS_HOST)


def fetch_wikipedia_content(search_query: str) -> dict:
    """Fetches wikipedia content for a given search_query"""
    try:
        # Search for most relevant article
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_query,
            "srlimit": 1,
        }

        url = f"{search_url}?{urllib.parse.urlencode(search_params)}"
        with urllib.request.urlopen(url) as response:
            search_data = json.loads(response.read().decode())

        if not search_data["query"]["search"]:
            return {
                "status": "error",
                "message": f"No Wikipedia article found for '{search_query}'",
            }

        # Get the normalized title from search results
        normalized_title = search_data["query"]["search"][0]["title"]

        # Now fetch the actual content with the normalized title
        content_params = {
            "action": "query",
            "format": "json",
            "titles": normalized_title,
            "prop": "extracts",
            "exintro": "true",
            "explaintext": "true",
            "redirects": 1,
        }

        url = f"{search_url}?{urllib.parse.urlencode(content_params)}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]

        if page_id == "-1":
            return {
                "status": "error",
                "message": f"No Wikipedia article found for '{search_query}'",
            }

        content = pages[page_id]["extract"].strip()
        return {
            "status": "success",
            "content": content,
            "title": pages[page_id]["title"],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# Define tool for LM Studio
WIKI_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_wikipedia_content",
        "description": (
            "Search Wikipedia and fetch the introduction of the most relevant article. "
            "Always use this if the user is asking for something that is likely on wikipedia. "
            "If the user has a typo in their search query, correct it before searching."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Search query for finding the Wikipedia article",
                },
            },
            "required": ["search_query"],
        },
    },
}


# Class for displaying the state of model processing
class Spinner:
    def __init__(self, message="Processing..."):
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.busy = False
        self.delay = 0.1
        self.message = message
        self.thread = None

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def _spin(self):
        while self.busy:
            self.write(f"\r{self.message} {next(self.spinner)}")
            time.sleep(self.delay)
        self.write("\r\033[K")  # Clear the line

    def __enter__(self):
        self.busy = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.busy = False
        time.sleep(self.delay)
        if self.thread:
            self.thread.join()
        self.write("\r")  # Move cursor to beginning of line


def chat_loop_official_sdk():
    """
    Main chat loop using the official LMStudio SDK.
    This demonstrates how to handle tool calls with the official SDK.
    """
    print("🚀 LMStudio Wikipedia Chatbot (Official SDK)")
    print("=" * 50)
    
    # Test connection first
    if not client.health_check():
        print("❌ LMStudio server is not responding!")
        print(f"Please ensure LMStudio is running at {LMS_HOST}")
        return
    
    print("✅ Connected to LMStudio server")
    print(f"📡 Host: {LMS_HOST}")
    print(f"🤖 Model: {MODEL}")
    
    # Create chat session with system message
    chat = client.get_chat(
        "You are an assistant that can retrieve Wikipedia articles. "
        "When asked about a topic, you can retrieve Wikipedia articles "
        "and cite information from them."
    )
    
    print(
        "\nAssistant: "
        "Hi! I can access Wikipedia to help answer your questions about history, "
        "science, people, places, or concepts - or we can just chat about "
        "anything else!"
    )
    print("(Type 'quit' to exit)")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            break

        try:
            # Add user message to chat
            chat.add_user_message(user_input)
            
            with Spinner("Thinking..."):
                # Get LLM instance and respond
                llm = client.get_llm(MODEL)
                
                # For tool use, we'll need to implement this differently
                # The official SDK might handle tools differently than OpenAI API
                # For now, let's demonstrate a simpler approach
                
                # Check if the user is asking about something that might be on Wikipedia
                wikipedia_keywords = [
                    "who is", "what is", "when was", "where is", "tell me about",
                    "explain", "history of", "definition of", "biography", "facts about"
                ]
                
                should_search_wikipedia = any(keyword in user_input.lower() for keyword in wikipedia_keywords)
                
                if should_search_wikipedia:
                    # Extract search query (simple approach)
                    search_query = user_input
                    for keyword in wikipedia_keywords:
                        search_query = search_query.lower().replace(keyword, "").strip()
                    
                    # Fetch Wikipedia content
                    wiki_result = fetch_wikipedia_content(search_query)
                    
                    # Display Wikipedia content
                    terminal_width = shutil.get_terminal_size().columns
                    print("\n" + "=" * terminal_width)
                    if wiki_result["status"] == "success":
                        print(f"\n📖 Wikipedia article: {wiki_result['title']}")
                        print("-" * terminal_width)
                        print(wiki_result["content"][:1000] + "..." if len(wiki_result["content"]) > 1000 else wiki_result["content"])
                    else:
                        print(f"\n❌ Error fetching Wikipedia content: {wiki_result['message']}")
                    print("=" * terminal_width + "\n")
                    
                    # Create enhanced prompt with Wikipedia context
                    if wiki_result["status"] == "success":
                        enhanced_prompt = f"""Based on this Wikipedia information about '{wiki_result['title']}':

{wiki_result['content']}

User question: {user_input}

Please provide a comprehensive answer using the Wikipedia information above."""
                        
                        response = llm.respond(enhanced_prompt)
                    else:
                        response = llm.respond(f"I couldn't find Wikipedia information about that topic. {user_input}")
                else:
                    # Regular chat response
                    response = llm.respond(user_input)
                
                print(f"\nAssistant: {response}")

        except Exception as e:
            print(
                f"\n❌ Error chatting with the LM Studio server!\n\n"
                f"Please ensure:\n"
                f"1. LM Studio server is running at {LMS_HOST}\n"
                f"2. Model '{MODEL}' is downloaded\n"
                f"3. Model '{MODEL}' is loaded, or that just-in-time model loading is enabled\n\n"
                f"Error details: {str(e)}\n"
                "See https://lmstudio.ai/docs/basics/server for more information"
            )
            break


def chat_loop_streaming():
    """
    Alternative chat loop demonstrating streaming with the official SDK.
    """
    print("\n🔄 Streaming Mode (Official SDK)")
    print("=" * 40)
    
    # Create LLM instance for streaming
    llm = client.get_llm(MODEL)
    chat_session = client.get_chat(
        "You are a helpful assistant. Be concise but informative."
    )
    
    print("Assistant: Hello! I'm ready to help. Ask me anything!")
    print("(Type 'quit' to exit streaming mode)")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            break

        try:
            print("\nAssistant: ", end="", flush=True)
            
            # Add user message to chat
            chat_session.add_user_message(user_input)
            
            # Stream response using our LLM implementation
            collected_response = ""
            try:
                # Use the streaming capability from our LLM
                from neo4j_lmstudio.core.llm import LMStudioLLM
                streaming_llm = LMStudioLLM(model_name=MODEL)
                
                for chunk in streaming_llm.stream(user_input, chat_session):
                    print(chunk, end="", flush=True)
                    collected_response += chunk
                    
            except Exception as stream_error:
                # Fallback to regular response if streaming fails
                response = llm.respond(user_input)
                print(response)
                collected_response = response
            
            print()  # New line after streaming completes
            
        except Exception as e:
            print(f"\n❌ Streaming error: {e}")
            break


def main():
    """Main function to run the demo."""
    print("🤖 LMStudio Wikipedia Demo with Official SDK")
    print("=" * 50)
    
    try:
        # Test basic connectivity
        print("🔍 Testing LMStudio connection...")
        if not client.validate_connection():
            print("❌ Cannot connect to LMStudio server")
            print(f"Please start LMStudio at {LMS_HOST}")
            return
        
        print("✅ LMStudio connection successful")
        
        # Show available options
        print("\nChoose demo mode:")
        print("1. Wikipedia integration (default)")
        print("2. Streaming chat")
        print("3. Both")
        
        choice = input("Enter choice (1-3, default=1): ").strip() or "1"
        
        if choice in ["1", "3"]:
            chat_loop_official_sdk()
        
        if choice in ["2", "3"]:
            chat_loop_streaming()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
