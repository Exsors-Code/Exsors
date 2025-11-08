#!/usr/bin/env python3
"""
Advanced decryption for JzProxy.lua_enc
Try multiple decryption methods including Lua bytecode detection
"""

def try_decrypt(data):
    methods_tried = []
    
    # Method 1: Simple XOR with position
    print("=== Method 1: XOR with position ===")
    result = bytearray()
    for i, byte in enumerate(data):
        result.append(byte ^ (i & 0xFF))
    
    if check_lua_signature(result):
        save_result(result, "xor_position")
        return result
    methods_tried.append("XOR with position")
    
    # Method 2: XOR with repeating key pattern
    print("\n=== Method 2: XOR with repeating key ===")
    # Common key lengths to try
    for key_len in [1, 2, 4, 8, 16, 32]:
        for start_key in range(min(256, 256//key_len)):
            key = bytes([(start_key + i) % 256 for i in range(key_len)])
            result = bytearray()
            for i, byte in enumerate(data):
                result.append(byte ^ key[i % len(key)])
            
            if check_lua_signature(result):
                print(f"Found with key: {key.hex()}")
                save_result(result, f"xor_key_{key.hex()}")
                return result
    
    # Method 3: Subtract offset
    print("\n=== Method 3: Subtract offset ===")
    for offset in range(256):
        result = bytearray((byte - offset) & 0xFF for byte in data)
        if check_lua_signature(result):
            print(f"Found with offset: {offset}")
            save_result(result, f"subtract_{offset}")
            return result
    
    # Method 4: Add offset
    print("\n=== Method 4: Add offset ===")
    for offset in range(256):
        result = bytearray((byte + offset) & 0xFF for byte in data)
        if check_lua_signature(result):
            print(f"Found with offset: {offset}")
            save_result(result, f"add_{offset}")
            return result
    
    # Method 5: XOR with incrementing position-based key
    print("\n=== Method 5: XOR with position-based key ===")
    for start in range(256):
        result = bytearray()
        for i, byte in enumerate(data):
            key = (start + i) & 0xFF
            result.append(byte ^ key)
        
        if check_lua_signature(result):
            print(f"Found with start: {start}")
            save_result(result, f"xor_inc_{start}")
            return result
    
    print("\nNo valid Lua signature found. Trying text-based detection...")
    
    # Try to find readable Lua code patterns
    for offset in range(256):
        result = bytearray((byte - offset) & 0xFF for byte in data)
        text = result[:5000].decode('utf-8', errors='ignore')
        if any(pattern in text for pattern in ['function', 'local ', 'return', 'end', 'if ', 'then']):
            print(f"Found Lua code patterns with offset: {offset}")
            save_result(result, f"text_subtract_{offset}")
            return result
    
    return None

def check_lua_signature(data):
    """Check if data starts with Lua bytecode signature"""
    # Lua 5.1: \x1bLua
    # Lua 5.2/5.3: \x1bLua\x52 or \x1bLua\x53
    if len(data) < 4:
        return False
    
    if data[:4] == b'\x1bLua':
        print(f"✓ Found Lua bytecode signature! Version bytes: {data[4:8].hex()}")
        return True
    
    # Also check for plain Lua text
    try:
        text = data[:1000].decode('utf-8', errors='strict')
        if 'function' in text or 'local ' in text:
            print("✓ Found Lua source code!")
            return True
    except:
        pass
    
    return False

def save_result(data, method_name):
    filename = f'/vercel/sandbox/decrypted_{method_name}.lua'
    with open(filename, 'wb') as f:
        f.write(data)
    print(f"Saved to: {filename}")
    
    # Show preview
    try:
        preview = data[:500].decode('utf-8', errors='ignore')
        print(f"Preview:\n{preview}\n")
    except:
        print(f"Binary preview (hex): {data[:100].hex()}\n")

def main():
    with open('/vercel/sandbox/uploads/JzProxy.lua_enc', 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    print(f"First 32 bytes (hex): {data[:32].hex()}")
    print(f"First 32 bytes (ascii): {data[:32]}\n")
    
    result = try_decrypt(data)
    
    if result:
        print("\n✓ Decryption successful!")
    else:
        print("\n✗ Could not decrypt the file automatically.")
        print("The file may use a custom encryption scheme.")

if __name__ == '__main__':
    main()
