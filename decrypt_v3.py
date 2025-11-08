#!/usr/bin/env python3
"""
Analyze the encryption pattern in detail
The header suggests: 68 69 5d 7b 7c 7d 7e 7f 80 81 82...
This looks like a substitution table
"""

def analyze_pattern(data):
    print("=== Analyzing encryption pattern ===\n")
    
    # Look at the first bytes
    header = data[:50]
    print(f"First 50 bytes (hex): {header.hex()}")
    print(f"First 50 bytes (dec): {[b for b in header]}")
    
    # Check if there's a pattern
    # 0x68 = 104, 0x69 = 105, 0x5d = 93, 0x7b = 123
    # Maybe it's a lookup table?
    
    # The sequence 7b 7c 7d 7e 7f 80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f 90 91 92 93 94 95 96 97
    # is consecutive from 0x7b to 0x97
    # This suggests bytes 0-255 are mapped to different values
    
    # Let's assume the first 256 bytes (or some portion) is a substitution table
    print("\n=== Checking if file starts with substitution table ===")
    
    # Common Lua file starts
    lua_starts = [
        b'--',  # Comment
        b'local ',
        b'function',
        b'return',
        b'if ',
        b'require',
        b'\x1bLua',  # Bytecode
    ]
    
    # Try to find where the actual data starts
    # The pattern suggests a 256-byte table might be at the start
    
    # Let's try: the first N bytes are a substitution table
    for table_size in [256, 512, 1024]:
        if len(data) < table_size + 100:
            continue
            
        print(f"\nTrying table size: {table_size}")
        sub_table = data[:table_size]
        encrypted_data = data[table_size:]
        
        # Create reverse lookup
        reverse_table = bytearray(256)
        for i in range(min(256, len(sub_table))):
            reverse_table[sub_table[i]] = i
        
        # Decrypt
        decrypted = bytearray()
        for byte in encrypted_data:
            decrypted.append(reverse_table[byte])
        
        # Check if it looks like Lua
        preview = decrypted[:500]
        try:
            text = preview.decode('utf-8', errors='ignore')
            if any(start.decode('utf-8', errors='ignore') in text for start in lua_starts if isinstance(start, bytes)):
                print(f"✓ Found Lua code with table size {table_size}!")
                print(f"Preview:\n{text[:500]}\n")
                
                with open(f'/vercel/sandbox/decrypted_table_{table_size}.lua', 'wb') as f:
                    f.write(decrypted)
                return decrypted
        except:
            pass
        
        # Check for bytecode
        if decrypted[:4] == b'\x1bLua':
            print(f"✓ Found Lua bytecode with table size {table_size}!")
            with open(f'/vercel/sandbox/decrypted_table_{table_size}.luac', 'wb') as f:
                f.write(decrypted)
            return decrypted
    
    # Maybe the whole file is encrypted with a simple substitution
    # Let's try to build the substitution table from the header pattern
    print("\n=== Trying to decrypt entire file as substitution cipher ===")
    
    # The pattern 68 69 5d suggests: 
    # encrypted[0] = 0x68 -> original[0] = ?
    # We need to figure out what the original sequence should be
    
    # If it's Lua source, it likely starts with printable ASCII
    # If it's Lua bytecode, it starts with \x1bLua (0x1b 0x4c 0x75 0x61)
    
    # Let's try: assume it should start with common Lua patterns
    for start_pattern in [b'\x1bLua', b'--[[', b'loca', b'func', b'retu']:
        print(f"\nTrying pattern: {start_pattern.hex()} ({start_pattern})")
        
        # Build partial substitution table from this assumption
        if len(start_pattern) > len(data):
            continue
        
        sub_table = bytearray(range(256))  # Identity mapping by default
        
        # Map the known bytes
        for i, byte in enumerate(start_pattern):
            encrypted_byte = data[i]
            sub_table[encrypted_byte] = byte
        
        # Decrypt
        decrypted = bytearray()
        for byte in data:
            decrypted.append(sub_table[byte])
        
        # Check result
        if decrypted[:len(start_pattern)] == start_pattern:
            print(f"✓ Pattern matches!")
            preview = decrypted[:1000]
            try:
                text = preview.decode('utf-8', errors='ignore')
                print(f"Preview:\n{text}\n")
                
                with open(f'/vercel/sandbox/decrypted_pattern_{start_pattern.hex()}.lua', 'wb') as f:
                    f.write(decrypted)
                    
                if b'function' in decrypted[:5000] or b'local' in decrypted[:5000]:
                    print("✓ Looks like valid Lua code!")
                    return decrypted
            except:
                print(f"Binary data (hex): {preview[:100].hex()}")
    
    return None

def main():
    with open('/vercel/sandbox/uploads/JzProxy.lua_enc', 'rb') as f:
        data = f.read()
    
    result = analyze_pattern(data)
    
    if not result:
        print("\n✗ Could not decrypt automatically.")
        print("\nThis file likely uses a custom encryption scheme specific to JzProxy.")
        print("You may need:")
        print("1. The original encryption tool/script")
        print("2. The encryption key")
        print("3. Documentation about the encryption method")

if __name__ == '__main__':
    main()
