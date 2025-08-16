# OpenAI API to Official LMStudio SDK Migration Guide

This guide demonstrates how to convert code from the OpenAI-compatible API to the official LMStudio SDK, using the Wikipedia chatbot example as a reference.

## Key Differences Overview

| Aspect | OpenAI-Compatible API | Official LMStudio SDK |
|--------|----------------------|----------------------|
| **Import** | `from openai import OpenAI` | `import lmstudio as lms` |
| **Client Setup** | `OpenAI(base_url="...", api_key="...")` | `lms.configure_default_client("host:port")` |
| **Basic Chat** | `client.chat.completions.create()` | `lms.llm().respond()` |
| **Streaming** | `stream=True` parameter | `lms.llm().respond_stream()` |
| **Chat Sessions** | Manual message management | `lms.Chat()` objects |
| **Tool Calling** | OpenAI tools format | SDK-specific tool handling |

## 1. Client Configuration

### Before (OpenAI-Compatible API)
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LMSTUDIO_API_HOST", "http://127.0.0.1:1234/v1"),
    api_key="lm-studio",
)
MODEL = "openai/gpt-oss-20b"
```

### After (Official LMStudio SDK)
```python
import lmstudio as lms
from dotenv import load_dotenv

load_dotenv()

# Configure the default client
LMS_HOST = os.getenv("LMSTUDIO_API_HOST", "localhost:1234")
lms.configure_default_client(LMS_HOST)

# Optional: Use our enhanced client wrapper
from neo4j_lmstudio.core.client import LMStudioClient
client = LMStudioClient(server_host=LMS_HOST)

MODEL = "openai/gpt-oss-20b"
```

## 2. Basic Chat Completion

### Before (OpenAI-Compatible API)
```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

### After (Official LMStudio SDK)
```python
# Method 1: Direct LLM usage
llm = lms.llm(MODEL)
response = llm.respond("Hello!")
print(response)

# Method 2: With chat session
chat = lms.Chat("You are a helpful assistant.")
chat.add_user_message("Hello!")
llm = lms.llm(MODEL)
response = llm.respond(chat)
print(response)

# Method 3: Using our enhanced client
response = client.respond("Hello!", model_name=MODEL)
print(response)
```

## 3. Streaming Responses

### Before (OpenAI-Compatible API)
```python
stream_response = client.chat.completions.create(
    model=MODEL, 
    messages=messages, 
    stream=True
)

collected_content = ""
for chunk in stream_response:
    if chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)
        collected_content += content
```

### After (Official LMStudio SDK)
```python
# Method 1: Direct streaming
llm = lms.llm(MODEL)
chat = lms.Chat()
chat.add_user_message("Your message here")

prediction_stream = llm.respond_stream(
    chat,
    on_message=chat.append,
)

collected_content = ""
for fragment in prediction_stream:
    print(fragment.content, end="", flush=True)
    collected_content += fragment.content

# Method 2: Using our enhanced LLM
from neo4j_lmstudio.core.llm import LMStudioLLM
streaming_llm = LMStudioLLM(model_name=MODEL)

collected_content = ""
for chunk in streaming_llm.stream("Your message here"):
    print(chunk, end="", flush=True)
    collected_content += chunk
```

## 4. Chat Session Management

### Before (OpenAI-Compatible API)
```python
# Manual message array management
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

# Add user message
messages.append({"role": "user", "content": user_input})

# Get response
response = client.chat.completions.create(
    model=MODEL,
    messages=messages
)

# Add assistant response
messages.append({
    "role": "assistant", 
    "content": response.choices[0].message.content
})
```

### After (Official LMStudio SDK)
```python
# Automatic session management with Chat object
chat = lms.Chat("You are a helpful assistant.")
llm = lms.llm(MODEL)

# Add user message and get response
chat.add_user_message(user_input)
response = llm.respond(chat)

# Chat object automatically maintains history
print(f"Chat history length: {len(chat.history)}")
```

## 5. Tool Calling (Advanced)

### Before (OpenAI-Compatible API)
```python
# Define tools in OpenAI format
tools = [{
    "type": "function",
    "function": {
        "name": "fetch_wikipedia_content",
        "description": "Search Wikipedia...",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {"type": "string"}
            },
            "required": ["search_query"]
        }
    }
}]

# Make request with tools
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = fetch_wikipedia_content(args["search_query"])
        # Add tool result to messages...
```

### After (Official LMStudio SDK)
```python
# Note: Official SDK may handle tools differently
# For now, we implement tool-like behavior manually

def is_wikipedia_query(user_input):
    """Check if input seems to request Wikipedia information."""
    keywords = ["who is", "what is", "tell me about", "explain"]
    return any(keyword in user_input.lower() for keyword in keywords)

def handle_wikipedia_request(user_input, llm):
    """Handle Wikipedia requests manually."""
    if is_wikipedia_query(user_input):
        # Extract search query
        search_query = extract_search_terms(user_input)
        
        # Fetch Wikipedia content
        wiki_result = fetch_wikipedia_content(search_query)
        
        if wiki_result["status"] == "success":
            # Create enhanced prompt with Wikipedia context
            enhanced_prompt = f"""Based on this Wikipedia information:

{wiki_result['content']}

User question: {user_input}

Please provide a comprehensive answer using the information above."""
            
            return llm.respond(enhanced_prompt)
    
    # Regular response
    return llm.respond(user_input)
```

## 6. Error Handling

### Before (OpenAI-Compatible API)
```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    print(f"OpenAI API error: {e}")
```

### After (Official LMStudio SDK)
```python
try:
    response = llm.respond(...)
except lms.LMStudioError as e:
    print(f"LMStudio SDK error: {e}")
except lms.LMStudioServerError as e:
    print(f"LMStudio server error: {e}")
except Exception as e:
    print(f"General error: {e}")
```

## 7. Connection Testing

### Before (OpenAI-Compatible API)
```python
try:
    # Test with a simple request
    test_response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "test"}],
        max_tokens=1
    )
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

### After (Official LMStudio SDK)
```python
# Method 1: Using our enhanced client
if client.health_check():
    print("Connection successful")
else:
    print("Connection failed")

# Method 2: Direct SDK test
try:
    llm = lms.llm(MODEL)
    test_response = llm.respond("test")
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

## 8. Model Management

### Before (OpenAI-Compatible API)
```python
# Limited model management through OpenAI API
try:
    models = client.models.list()
    print(f"Available models: {[m.id for m in models.data]}")
except Exception as e:
    print(f"Could not list models: {e}")
```

### After (Official LMStudio SDK)
```python
# Better model management with official SDK
try:
    # List downloaded models
    downloaded_models = lms.list_downloaded_models()
    print(f"Downloaded models: {len(downloaded_models)}")
    
    # List loaded models
    loaded_models = lms.list_loaded_models()
    print(f"Loaded models: {len(loaded_models)}")
    
    # Using our enhanced client
    downloaded = client.list_downloaded_models()
    loaded = client.list_loaded_models()
    
except Exception as e:
    print(f"Model listing error: {e}")
```

## Benefits of Official SDK Migration

### 1. **Native Performance**
- Direct WebSocket connections instead of HTTP REST
- Better streaming performance
- Reduced connection overhead

### 2. **Enhanced Features**
- Native chat session management
- Better model loading and management
- Access to LMStudio-specific optimizations

### 3. **Improved Error Handling**
- SDK-specific error types
- Better error messages and debugging
- More reliable connection management

### 4. **Future-Proof Development**
- Alignment with LMStudio's roadmap
- Access to new features as they're released
- Better long-term support and maintenance

## Migration Checklist

- [ ] Replace OpenAI imports with LMStudio SDK imports
- [ ] Update client configuration to use `lms.configure_default_client()`
- [ ] Convert `chat.completions.create()` calls to `lms.llm().respond()`
- [ ] Update streaming code to use SDK streaming methods
- [ ] Replace manual message management with `lms.Chat()` objects
- [ ] Update tool calling to use SDK-appropriate patterns
- [ ] Enhance error handling with SDK-specific exceptions
- [ ] Test all functionality with the new SDK
- [ ] Update documentation and examples

This migration guide should help you convert any existing OpenAI-compatible LMStudio code to use the official SDK effectively!
