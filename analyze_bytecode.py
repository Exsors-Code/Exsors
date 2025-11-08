#!/usr/bin/env python3
"""
Analyze Lua bytecode structure
"""

def analyze_lua_bytecode(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print("="*70)
    print("LUA BYTECODE ANALYSIS")
    print("="*70)
    
    if len(data) < 12:
        print("File too small to be valid Lua bytecode")
        return
    
    # Parse Lua bytecode header
    pos = 0
    
    # Signature
    signature = data[pos:pos+4]
    pos += 4
    print(f"\nSignature: {signature.hex()} ({signature})")
    
    if signature != b'\x1bLua':
        print("✗ Invalid Lua bytecode signature!")
        return
    
    print("✓ Valid Lua bytecode signature")
    
    # Version
    version = data[pos]
    pos += 1
    lua_version = f"5.{version - 0x50}" if version >= 0x50 else f"Unknown ({version})"
    print(f"Lua Version: {lua_version} (byte: 0x{version:02x})")
    
    # Format version
    format_ver = data[pos]
    pos += 1
    print(f"Format Version: {format_ver}")
    
    # Endianness, int size, size_t size, instruction size, lua_Number size, integral flag
    if pos + 6 <= len(data):
        endianness = data[pos]
        pos += 1
        int_size = data[pos]
        pos += 1
        size_t_size = data[pos]
        pos += 1
        instruction_size = data[pos]
        pos += 1
        lua_number_size = data[pos]
        pos += 1
        integral_flag = data[pos]
        pos += 1
        
        print(f"\nBytecode Properties:")
        print(f"  Endianness: {'Little' if endianness == 1 else 'Big' if endianness == 0 else 'Unknown'}")
        print(f"  Int size: {int_size} bytes")
        print(f"  size_t size: {size_t_size} bytes")
        print(f"  Instruction size: {instruction_size} bytes")
        print(f"  Lua Number size: {lua_number_size} bytes")
        print(f"  Integral flag: {integral_flag}")
    
    # Try to extract strings (common in Lua bytecode)
    print(f"\n{'='*70}")
    print("EXTRACTING READABLE STRINGS")
    print("="*70)
    
    strings = []
    i = 0
    while i < len(data) - 4:
        # Look for length-prefixed strings (common in Lua bytecode)
        # Try to find printable ASCII strings
        if data[i] >= 32 and data[i] < 127:
            string_start = i
            string_len = 0
            while i < len(data) and data[i] >= 32 and data[i] < 127 and string_len < 200:
                string_len += 1
                i += 1
            
            if string_len >= 4:  # Minimum string length
                try:
                    s = data[string_start:string_start+string_len].decode('ascii')
                    if len(s.strip()) > 0 and not all(c in '\\x00\\xff' for c in s):
                        strings.append(s)
                except:
                    pass
        i += 1
    
    # Remove duplicates and sort
    strings = sorted(set(strings))
    
    print(f"\nFound {len(strings)} potential strings:\n")
    
    # Group strings by type
    functions = [s for s in strings if 'function' in s.lower() or s.startswith('_') or '(' in s]
    variables = [s for s in strings if s.isidentifier() and len(s) > 2]
    urls = [s for s in strings if 'http' in s.lower() or '://' in s or '.com' in s or '.net' in s]
    paths = [s for s in strings if '/' in s or '\\' in s]
    others = [s for s in strings if s not in functions + variables + urls + paths]
    
    if urls:
        print("URLs/Domains:")
        for s in urls[:20]:
            print(f"  {s}")
    
    if functions:
        print("\nPossible Functions:")
        for s in functions[:20]:
            print(f"  {s}")
    
    if variables:
        print("\nPossible Variables:")
        for s in variables[:30]:
            print(f"  {s}")
    
    if paths:
        print("\nPaths:")
        for s in paths[:20]:
            print(f"  {s}")
    
    if others:
        print("\nOther Strings:")
        for s in others[:30]:
            if len(s) > 3:
                print(f"  {s}")
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("="*70)
    print(f"File size: {len(data):,} bytes")
    print(f"Lua version: {lua_version}")
    print(f"Total strings found: {len(strings)}")
    print(f"\nThe file has been successfully decrypted to Lua bytecode.")
    print(f"To get the full source code, you would need a Lua decompiler like:")
    print(f"  - unluac (requires Java)")
    print(f"  - luadec")
    print(f"  - Online decompilers")
    
    # Save strings to a file
    with open('/vercel/sandbox/extracted_strings.txt', 'w') as f:
        f.write("Extracted strings from JzProxy.lua bytecode\n")
        f.write("="*70 + "\n\n")
        for s in strings:
            f.write(s + "\n")
    
    print(f"\n✓ Extracted strings saved to: /vercel/sandbox/extracted_strings.txt")

if __name__ == '__main__':
    analyze_lua_bytecode('/vercel/sandbox/JzProxy_decrypted.luac')
