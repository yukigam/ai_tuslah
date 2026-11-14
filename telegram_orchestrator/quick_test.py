"""Quick standalone test for Telegram Orchestrator Integration."""

import asyncio
import sys
import os

# Add the package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_orchestrator import TelegramOrchestratorIntegration


async def quick_test():
    """Quick standalone test."""
    print("=" * 60)
    print("Telegram Orchestrator Integration Quick Test")
    print("=" * 60)
    
    # Create integration with default agents
    integration = TelegramOrchestratorIntegration()
    
    # Test messages
    test_messages = [
        ("user123", "Generate a post about AI technology"),
        ("user456", "Fix this code: body_lower = \"\"\n    try:"),
        ("user789", "Check database status"),
    ]
    
    print("\nProcessing test messages through orchestrator...\n")
    
    for user_id, message in test_messages:
        response = await integration.handle_message(
            user_id=int(user_id.split('user')[1]),
            user_message=message,
            chat_id=999999  # dummy chat ID
        )
        print(f"👤 User {user_id}: {message}")
        print(f"🤖 Bot: {response[:150]}...")
        print("-" * 60)
    
    # Test concurrent processing
    print("\n" + "=" * 60)
    print("Concurrent Processing Test")
    print("=" * 60)
    
    concurrent_messages = [
        ("user123", "Post about Python"),
        ("user456", "Fix: x = 1"),
        ("user789", "Check database"),
    ]
    
    responses = await integration.process_concurrent_messages(concurrent_messages, chat_id=999999)
    for i, (_, msg) in enumerate(concurrent_messages):
        print(f"⚡ Message: {msg}")
        print(f"   Response: {responses[i][:80]}...")
    
    print("\n" + "=" * 60)
    print("Quick test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(quick_test())