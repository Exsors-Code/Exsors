#!/usr/bin/env python3
"""
Decrypt JzProxy.lua_enc file
Analyzing the header pattern to determine encryption method
"""

def analyze_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    print(f"First 100 bytes (hex): {data[:100].hex()}")
    print(f"First 100 bytes (raw): {data[:100]}")
    
    # Check if it's a simple XOR cipher
    # The pattern 68 69 5d 7b 7c 7d 7e 7f 80... suggests XOR with incrementing key
    
    # Try XOR with different keys
    print("\n--- Trying XOR decryption ---")
    
    # Method 1: XOR with incrementing byte starting from 0
    result1 = bytearray()
    for i, byte in enumerate(data):
        result1.append(byte ^ (i & 0xFF))
    
    # Check if result looks like Lua code
    if b'function' in result1[:1000] or b'local' in result1[:1000] or b'--' in result1[:1000]:
        print("Method 1 (XOR with index) looks promising!")
        with open('/vercel/sandbox/decrypted_method1.lua', 'wb') as f:
            f.write(result1)
        print("Saved to decrypted_method1.lua")
        print(f"First 500 chars:\n{result1[:500].decode('utf-8', errors='ignore')}")
    
    # Method 2: XOR with single byte key
    for key in range(256):
        result2 = bytearray(byte ^ key for byte in data[:1000])
        if b'function' in result2 or b'local' in result2:
            print(f"\nMethod 2 (XOR with key {key}) looks promising!")
            full_result = bytearray(byte ^ key for byte in data)
            with open(f'/vercel/sandbox/decrypted_key_{key}.lua', 'wb') as f:
                f.write(full_result)
            print(f"First 500 chars:\n{full_result[:500].decode('utf-8', errors='ignore')}")
            break
    
    # Method 3: Check if it's just offset by a constant
    for offset in range(1, 256):
        result3 = bytearray((byte - offset) & 0xFF for byte in data[:1000])
        if b'function' in result3 or b'local' in result3 or b'--' in result3:
            print(f"\nMethod 3 (Subtract {offset}) looks promising!")
            full_result = bytearray((byte - offset) & 0xFF for byte in data)
            with open(f'/vercel/sandbox/decrypted_offset_{offset}.lua', 'wb') as f:
                f.write(full_result)
            print(f"First 500 chars:\n{full_result[:500].decode('utf-8', errors='ignore')}")
            break

if __name__ == '__main__':
    analyze_file('/vercel/sandbox/uploads/JzProxy.lua_enc')
