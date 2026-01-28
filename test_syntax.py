# Test script to check syntax errors in translated code
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing syntax of translated code...")

# Test importing core modules
try:
    from open_llm_vtuber.server import WebSocketServer
    print("✓ Successfully imported WebSocketServer")
except Exception as e:
    print(f"✗ Failed to import WebSocketServer: {e}")

try:
    from open_llm_vtuber.routes import init_client_ws_route
    print("✓ Successfully imported init_client_ws_route")
except Exception as e:
    print(f"✗ Failed to import init_client_ws_route: {e}")

try:
    from open_llm_vtuber.service_context import ServiceContext
    print("✓ Successfully imported ServiceContext")
except Exception as e:
    print(f"✗ Failed to import ServiceContext: {e}")

try:
    from open_llm_vtuber.utils.sentence_divider import SentenceDivider
    print("✓ Successfully imported SentenceDivider")
except Exception as e:
    print(f"✗ Failed to import SentenceDivider: {e}")

print("Syntax test completed!")
