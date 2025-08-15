#!/usr/bin/env python3
"""
Test script for LM Studio chat completion
"""

import sys
import os

# Add the genai-fundamentals directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'genai-fundamentals'))

from lmstudio_client import get_lmstudio_llm, LMStudioLLM, client

def test_chat_completion():
    print('Testing LM Studio chat completion...')
    
    try:
        # Test 1: Direct model usage
        print('\n=== Test 1: Direct model usage ===')
        model_name = get_lmstudio_llm()
        print(f'Got model: {model_name}')
        
        messages = [{"role": "user", "content": "Say hello in exactly 5 words."}]
        print('Sending request to model...')
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
        )
        print(f'Response: {response.choices[0].message.content}')
        
        # Test 2: LMStudioLLM wrapper
        print('\n=== Test 2: LMStudioLLM wrapper ===')
        llm = LMStudioLLM()
        print('Invoking LLM wrapper...')
        response = llm.invoke('Count from 1 to 5.')
        print(f'LLM Response: {response}')
        
        print('\n✅ Chat completion tests successful!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False
    
    return True

if __name__ == '__main__':
    success = test_chat_completion()
    sys.exit(0 if success else 1)
