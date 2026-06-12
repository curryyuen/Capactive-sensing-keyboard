# main.py - Main program for ESP32-C3
# Fixed script selection display

import gc
import time
import sys
import os

# ========== DUCKY SCRIPT EXECUTOR ==========
class DuckyExecutor:
    """Execute Ducky Script commands"""
    
    def __init__(self):
        self.default_delay = 100  # ms between commands
    
    def execute_script(self, filename):
        """Execute a Ducky Script file"""
        try:
            # Try to open from /scripts folder first
            filepath = None
            if self._file_exists(f"/scripts/{filename}"):
                filepath = f"/scripts/{filename}"
            elif self._file_exists(filename):
                filepath = filename
            else:
                print(f"[ERROR] Script not found: {filename}")
                return False
            
            with open(filepath, "r") as f:
                script_lines = f.readlines()
            
            print(f"\n" + "="*50)
            print(f"Executing script: {filename}")
            print("="*50)
            print(f"Total commands: {len(script_lines)}")
            print("Starting execution...\n")
            
            line_num = 0
            for line in script_lines:
                line_num += 1
                original_line = line
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('REM'):
                    continue
                
                # Parse command
                if line.upper().startswith('DELAY'):
                    parts = line.split()
                    if len(parts) > 1:
                        delay_ms = int(parts[1])
                        print(f"[{line_num}] DELAY {delay_ms}ms")
                        time.sleep_ms(delay_ms)
                
                elif line.upper().startswith('STRING'):
                    text = line[7:]  # Remove 'STRING '
                    print(f"[{line_num}] TYPE: \"{text}\"")
                    self._type_string(text)
                
                elif line.upper().startswith('GUI') or line.upper().startswith('WINDOWS'):
                    parts = line.split()
                    key = parts[1] if len(parts) > 1 else ''
                    print(f"[{line_num}] WIN+{key.upper()}")
                    self._press_winkey(key)
                
                elif line.upper().startswith('CTRL'):
                    parts = line.split()
                    key = parts[1] if len(parts) > 1 else ''
                    print(f"[{line_num}] CTRL+{key.upper()}")
                    self._press_ctrl(key)
                
                elif line.upper().startswith('ALT'):
                    parts = line.split()
                    key = parts[1] if len(parts) > 1 else ''
                    print(f"[{line_num}] ALT+{key.upper()}")
                    self._press_alt(key)
                
                elif line.upper() == 'ENTER':
                    print(f"[{line_num}] ENTER")
                    self._type_string('\n')
                
                elif line.upper() == 'TAB':
                    print(f"[{line_num}] TAB")
                    self._type_string('\t')
                
                elif line.upper() == 'SPACE':
                    print(f"[{line_num}] SPACE")
                    self._type_string(' ')
                
                elif line.upper().startswith('DEFAULT_DELAY'):
                    parts = line.split()
                    if len(parts) > 1:
                        self.default_delay = int(parts[1])
                        print(f"[{line_num}] DEFAULT_DELAY set to {self.default_delay}ms")
                
                else:
                    # Unknown command - treat as comment
                    print(f"[{line_num}] SKIP: {line[:50]}")
                
                # Small delay between commands
                time.sleep_ms(self.default_delay)
            
            print(f"\n" + "="*50)
            print("Script execution completed!")
            print("="*50)
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Failed to execute script: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def _file_exists(self, path):
        """Check if file exists"""
        try:
            os.stat(path)
            return True
        except:
            return False
    
    def _type_string(self, text):
        """Type a string character by character"""
        for char in text:
            if char == '\n':
                print("[ENTER]")
            elif char == '\t':
                print("[TAB]")
            else:
                print(char, end='')
            time.sleep_ms(10)
        if text and text != '\n' and text != '\t':
            print()
    
    def _press_winkey(self, key):
        """Press Windows key combination"""
        print(f"  [SIMULATED] Windows + {key}")
        if key == 'r':
            print("  > Would open Run dialog")
        elif key == 'e':
            print("  > Would open File Explorer")
        elif key == 'd':
            print("  > Would show desktop")
    
    def _press_ctrl(self, key):
        """Press Ctrl key combination"""
        print(f"  [SIMULATED] Ctrl+{key}")
        if key == 's':
            print("  > Would save file")
        elif key == 'c':
            print("  > Would copy")
        elif key == 'v':
            print("  > Would paste")
    
    def _press_alt(self, key):
        """Press Alt key combination"""
        print(f"  [SIMULATED] Alt+{key}")
        if key == 'f4':
            print("  > Would close window")
        elif key == 'tab':
            print("  > Would switch window")

def list_scripts():
    """List all available scripts"""
    scripts = []
    
    # Check /scripts folder
    try:
        for item in os.listdir("/scripts"):
            if item.endswith(".duck") or item.endswith(".txt"):
                if item != "pass.txt":  # Exclude password file
                    scripts.append(item)
    except Exception as e:
        print(f"Debug: Error reading /scripts: {e}")
    
    # Also check current directory (excluding web.py and main.py)
    try:
        for item in os.listdir():
            if (item.endswith(".duck") or item.endswith(".txt")) and item not in scripts:
                if item not in ["web.py", "main.py", "pass.txt"]:
                    scripts.append(item)
    except Exception as e:
        print(f"Debug: Error reading current dir: {e}")
    
    return sorted(scripts)

def get_script_size(filename):
    """Get file size in bytes"""
    try:
        if _file_exists(f"/scripts/{filename}"):
            stat = os.stat(f"/scripts/{filename}")
            return stat[6]
        elif _file_exists(filename):
            stat = os.stat(filename)
            return stat[6]
    except:
        pass
    return 0

def _file_exists(path):
    """Check if file exists"""
    try:
        os.stat(path)
        return True
    except:
        return False

def show_menu():
    """Show main menu"""
    print("\n" + "="*50)
    print("DUCKY SCRIPT MANAGER - MAIN MENU")
    print("="*50)
    print("1. Start Web Server")
    print("2. Run a Ducky Script")
    print("3. List Available Scripts")
    print("4. Delete a Script")
    print("5. View Script Content")
    print("6. Check Storage Info")
    print("7. Exit to REPL")
    print("="*50)

def run_script_interactive():
    """Interactive script runner"""
    print("\n" + "-"*50)
    print("RUN DUCKY SCRIPT")
    print("-"*50)
    
    scripts = list_scripts()
    
    # Debug output
    print(f"Debug: Found {len(scripts)} script(s)")
    
    if not scripts:
        print("\n[!] No scripts found!")
        print("    Create scripts using option 1 (Web Server)")
        print("    Then create .duck files in /scripts folder")
        print("\nTroubleshooting:")
        print("  1. Check if /scripts folder exists")
        print("  2. Verify files have .duck or .txt extension")
        print("  3. Use option 3 to list scripts first")
        input("\nPress Enter to continue...")
        return
    
    # Display scripts
    print("\nAvailable scripts:")
    for i, script in enumerate(scripts, 1):
        size = get_script_size(script)
        size_str = f"({size} bytes)" if size > 0 else ""
        print(f"  {i}. {script} {size_str}")
    
    print(f"  {len(scripts)+1}. Back to menu")
    print()  # Empty line for clarity
    
    try:
        choice = input(f"Select script (1-{len(scripts)+1}): ")
        
        if choice.isdigit():
            idx = int(choice) - 1
            
            if 0 <= idx < len(scripts):
                print(f"\nSelected: {scripts[idx]}")
                confirm = input(f"Execute '{scripts[idx]}'? (y/N): ")
                
                if confirm.lower() == 'y':
                    executor = DuckyExecutor()
                    executor.execute_script(scripts[idx])
                else:
                    print("Execution cancelled.")
            
            elif idx == len(scripts):
                print("Returning to menu...")
                return
            
            else:
                print(f"Invalid selection: {choice}")
        
        else:
            print(f"Invalid input: {choice}")
    
    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
    
    input("\nPress Enter to continue...")

def delete_script_interactive():
    """Delete a script interactively"""
    print("\n" + "-"*50)
    print("DELETE SCRIPT")
    print("-"*50)
    
    scripts = list_scripts()
    
    if not scripts:
        print("\n[!] No scripts found to delete.")
        input("\nPress Enter to continue...")
        return
    
    print("\nSelect script to delete:")
    for i, script in enumerate(scripts, 1):
        print(f"  {i}. {script}")
    print(f"  {len(scripts)+1}. Cancel")
    
    try:
        choice = input(f"\nSelect script (1-{len(scripts)+1}): ")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(scripts):
                print(f"\nSelected: {scripts[idx]}")
                confirm = input(f"Delete '{scripts[idx]}'? (y/N): ")
                if confirm.lower() == 'y':
                    try:
                        # Try to delete from /scripts first
                        if _file_exists(f"/scripts/{scripts[idx]}"):
                            os.remove(f"/scripts/{scripts[idx]}")
                            print(f"[+] Deleted: /scripts/{scripts[idx]}")
                        elif _file_exists(scripts[idx]):
                            os.remove(scripts[idx])
                            print(f"[+] Deleted: {scripts[idx]}")
                        else:
                            print("[-] File not found")
                    except Exception as e:
                        print(f"[-] Delete failed: {e}")
                else:
                    print("Cancelled.")
            elif idx == len(scripts):
                return
    except KeyboardInterrupt:
        print("\nCancelled.")
    
    input("\nPress Enter to continue...")

def view_script_interactive():
    """View script content"""
    print("\n" + "-"*50)
    print("VIEW SCRIPT")
    print("-"*50)
    
    scripts = list_scripts()
    
    if not scripts:
        print("\n[!] No scripts found to view.")
        input("\nPress Enter to continue...")
        return
    
    print("\nSelect script to view:")
    for i, script in enumerate(scripts, 1):
        print(f"  {i}. {script}")
    print(f"  {len(scripts)+1}. Cancel")
    
    try:
        choice = input(f"\nSelect script (1-{len(scripts)+1}): ")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(scripts):
                try:
                    # Try to read from /scripts first
                    if _file_exists(f"/scripts/{scripts[idx]}"):
                        filepath = f"/scripts/{scripts[idx]}"
                    else:
                        filepath = scripts[idx]
                    
                    with open(filepath, "r") as f:
                        content = f.read()
                    
                    print("\n" + "="*50)
                    print(f"Content of: {scripts[idx]}")
                    print("="*50)
                    print(content)
                    print("="*50)
                except Exception as e:
                    print(f"[-] Failed to read: {e}")
            elif idx == len(scripts):
                return
    except KeyboardInterrupt:
        print("\nCancelled.")
    
    input("\nPress Enter to continue...")

def show_storage_info():
    """Show storage information"""
    print("\n" + "="*50)
    print("STORAGE INFORMATION")
    print("="*50)
    
    # Show filesystem info
    try:
        stat = os.statvfs('/')
        block_size = stat[0]
        total_blocks = stat[2]
        free_blocks = stat[3]
        total = total_blocks * block_size
        free = free_blocks * block_size
        used = total - free
        
        print(f"Total space: {total // 1024} KB")
        print(f"Used space: {used // 1024} KB")
        print(f"Free space: {free // 1024} KB")
    except Exception as e:
        print(f"Unable to read filesystem info: {e}")
    
    # Show RAM info
    print(f"\nRAM free: {gc.mem_free()} bytes")
    print(f"RAM allocated: {gc.mem_alloc()} bytes")
    
    # List all scripts with sizes
    scripts = list_scripts()
    if scripts:
        print(f"\nScripts in storage:")
        for script in scripts:
            size = get_script_size(script)
            print(f"  - {script}: {size} bytes")
            
            # Show first few lines as preview
            try:
                if _file_exists(f"/scripts/{script}"):
                    filepath = f"/scripts/{script}"
                else:
                    filepath = script
                
                with open(filepath, "r") as f:
                    first_line = f.readline().strip()
                    if first_line:
                        print(f"    Preview: {first_line[:50]}")
            except:
                pass
    else:
        print("\nNo scripts found in storage")
    
    print("="*50)
    input("\nPress Enter to continue...")

def start_web_server():
    """Start the web server"""
    try:
        import web
        print("\nStarting web server...")
        print("Web interface available at: http://192.168.4.1")
        print("Press Ctrl+C to stop the server and return to menu")
        print("-"*50)
        web.start_server()
    except KeyboardInterrupt:
        print("\n\n[!] Web server stopped.")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to start web server: {e}")
        print("Make sure web.py is uploaded to the device")
        return False
    return True

# ========== MAIN PROGRAM ==========
def main():
    print("\n" + "="*50)
    print("ESP32-C3 Ducky Script Manager v1.0")
    print("="*50)
    print(f"Free RAM: {gc.mem_free()} bytes")
    
    # Create scripts folder if it doesn't exist
    try:
        os.mkdir("/scripts")
        print("[+] Created /scripts folder")
    except:
        pass
    
    # Show existing scripts
    scripts = list_scripts()
    if scripts:
        print(f"\n[+] Found {len(scripts)} script(s):")
        for script in scripts:
            size = get_script_size(script)
            print(f"    - {script} ({size} bytes)")
    else:
        print("\n[!] No scripts found. Create one using the web server.")
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            start_web_server()
        
        elif choice == '2':
            run_script_interactive()
        
        elif choice == '3':
            scripts = list_scripts()
            if scripts:
                print("\nAvailable scripts:")
                for script in scripts:
                    size = get_script_size(script)
                    print(f"  - {script} ({size} bytes)")
            else:
                print("\nNo scripts found.")
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            delete_script_interactive()
        
        elif choice == '5':
            view_script_interactive()
        
        elif choice == '6':
            show_storage_info()
        
        elif choice == '7':
            print("\nExiting to REPL...")
            print("Type Ctrl+D to soft reset or upload new code")
            break
        
        else:
            print("\nInvalid choice! Please enter 1-7")
            time.sleep(1)
        
        # Clean up memory
        gc.collect()
        print()  # Empty line for better readability

# Run main function
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import sys
        sys.print_exception(e)
