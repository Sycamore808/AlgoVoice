#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Wind Connection
"""
import sys

print("="*60)
print("Testing Wind Connection")
print("="*60)
print()

# Step 1: Check WindPy
print("[Step 1/3] Checking WindPy installation...")
try:
    import WindPy
    print("✓ WindPy installed")
    try:
        print(f"  Version: {WindPy.__version__}")
    except:
        print("  Version: Unknown")
    print(f"  Path: {WindPy.__file__}")
except ImportError as e:
    print("✗ WindPy NOT installed")
    print(f"  Error: {e}")
    print()
    print("Please install WindPy:")
    print("  Run: install_windpy.bat")
    print("  Or: pip install WindPy")
    sys.exit(1)

print()

# Step 2: Import Wind API
print("[Step 2/3] Importing Wind API...")
try:
    from WindPy import w
    print("✓ Wind API imported")
except Exception as e:
    print("✗ Failed to import Wind API")
    print(f"  Error: {e}")
    sys.exit(1)

print()

# Step 3: Test connection
print("[Step 3/3] Connecting to Wind Terminal...")
print()

try:
    result = w.start()
    
    print(f"Connection Result:")
    print(f"  ErrorCode: {result.ErrorCode}")
    
    if result.ErrorCode == 0:
        print()
        print("="*60)
        print("SUCCESS! Wind Connection Established!")
        print("="*60)
        print()
        print("Wind Terminal is ready to use.")
        print()
        
        # Quick test
        print("Testing data query...")
        test = w.wsd("000001.SZ", "close", "2024-01-01", "2024-01-05")
        if test.ErrorCode == 0:
            print(f"✓ Query test passed ({len(test.Times)} data points)")
        else:
            print(f"✗ Query failed: {test.Data}")
        
        print()
        print("Next step: Run download_data.bat")
        
    else:
        print()
        print("="*60)
        print("FAILED! Wind Connection Failed")
        print("="*60)
        print()
        print("Possible reasons:")
        print("  1. Wind Terminal is not running")
        print("  2. Not logged in")
        print("  3. Network issue")
        print()
        print("Please:")
        print("  1. Open Wind Terminal")
        print("  2. Login")
        print("  3. Try again")
        sys.exit(1)
        
except Exception as e:
    print()
    print("="*60)
    print("ERROR! Exception occurred")
    print("="*60)
    print()
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
finally:
    try:
        w.stop()
    except:
        pass

print()
print("="*60)








