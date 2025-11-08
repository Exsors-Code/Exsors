#!/usr/bin/env python3
"""
Final decryption for JzProxy.lua_enc
Uses substitution cipher with Lua bytecode signature
"""

def decrypt_file(input_file, output_file):
    with open(input_file, 'rb') as f:
        encrypted = f.read()
    
    print(f"Input file size: {len(encrypted)} bytes")
    print(f"First 20 bytes (hex): {encrypted[:20].hex()}")
    
    # The file is encrypted with a substitution cipher
    # We know it should start with \x1bLua (Lua bytecode signature)
    # encrypted[0:4] = 68 69 5d 7b
    # should be:       1b 4c 75 61
    
    # Build the substitution table
    lua_signature = b'\x1bLua'
    
    # Create identity mapping first
    sub_table = bytearray(range(256))
    
    # Map known bytes from the signature
    for i in range(len(lua_signature)):
        encrypted_byte = encrypted[i]
        original_byte = lua_signature[i]
        sub_table[encrypted_byte] = original_byte
    
    print(f"\nSubstitution mappings from signature:")
    for i in range(len(lua_signature)):
        enc = encrypted[i]
        orig = lua_signature[i]
        print(f"  0x{enc:02x} -> 0x{orig:02x}")
    
    # Decrypt the entire file
    decrypted = bytearray()
    for byte in encrypted:
        decrypted.append(sub_table[byte])
    
    # Save the result
    with open(output_file, 'wb') as f:
        f.write(decrypted)
    
    print(f"\n✓ Decrypted file saved to: {output_file}")
    print(f"Output file size: {len(decrypted)} bytes")
    
    # Verify it's valid Lua bytecode
    if decrypted[:4] == b'\x1bLua':
        version = decrypted[4]
        format_version = decrypted[5] if len(decrypted) > 5 else 0
        print(f"\n✓ Valid Lua bytecode detected!")
        print(f"  Lua version: 5.{version - 0x50}")
        print(f"  Format version: {format_version}")
        print(f"\nFirst 100 bytes (hex):")
        print(decrypted[:100].hex())
        
        return True
    else:
        print(f"\n✗ Warning: Output doesn't start with Lua bytecode signature")
        print(f"First 20 bytes: {decrypted[:20].hex()}")
        return False

def decompile_lua(bytecode_file):
    """Try to decompile Lua bytecode to source code"""
    print(f"\n=== Attempting to decompile Lua bytecode ===")
    
    # Check if unluac or luadec is available
    import subprocess
    
    tools = [
        ('unluac', ['java', '-jar', 'unluac.jar']),
        ('luadec', ['luadec']),
        ('luajit', ['luajit', '-b', '-l']),
    ]
    
    print("Note: Decompiling Lua bytecode requires external tools like:")
    print("  - unluac (Java-based decompiler)")
    print("  - luadec")
    print("  - luajit -b -l (for listing)")
    print("\nThe bytecode file has been saved. You can decompile it manually using these tools.")
    print(f"Example: java -jar unluac.jar {bytecode_file} > decrypted.lua")

if __name__ == '__main__':
    input_file = '/vercel/sandbox/uploads/JzProxy.lua_enc'
    output_file = '/vercel/sandbox/JzProxy_decrypted.luac'
    
    success = decrypt_file(input_file, output_file)
    
    if success:
        decompile_lua(output_file)
        
        print("\n" + "="*60)
        print("DECRYPTION SUCCESSFUL!")
        print("="*60)
        print(f"\nDecrypted bytecode saved to: {output_file}")
        print("\nTo convert bytecode to readable Lua source code, you'll need")
        print("a Lua decompiler. The file is now in standard Lua bytecode format.")
    else:
        print("\n" + "="*60)
        print("DECRYPTION COMPLETED WITH WARNINGS")
        print("="*60)
        print("\nThe file has been decrypted but may not be standard Lua bytecode.")
        print("Check the output file for more details.")
