#!/usr/bin/env python3
"""
HamppServer - Simple Local Server Manager
Author: Md Habibur Rahman
Version: 2.0.0

This is the main entry point for HamppServer.
Just run: python3 hampp.py (starts interactive mode)
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import hampp modules
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

def main():
    try:
        from hampp.cli.main import main as cli_main
        
        # If no arguments provided, start interactive mode automatically
        if len(sys.argv) == 1:
            sys.argv.append('interactive')
        
        cli_main()
        
    except ImportError as e:
        print(f"❌ Error: Could not import required modules: {e}")
        print()
        print("💡 Please install the required dependencies:")
        print("   pip install click rich pyyaml jinja2 psutil requests")
        print()
        print("   Or run the installer:")
        print("   ./install")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
