# web.py - Web server for Ducky Script Manager
# Save this as web.py on your ESP32-C3

import network
import socket
import os
import gc
import time

# ========== CONFIGURATION ==========
AP_SSID = "DuckyScriptManager"
AP_PASSWORD = "ducky123"
HTTP_PORT = 80
MAX_FILE_SIZE = 32768
ALLOWED_EXTENSIONS = [".duck", ".txt"]

# ========== STORAGE MANAGEMENT ==========
def init_storage():
    try:
        os.mkdir("/scripts")
    except:
        pass

def get_storage_info():
    stat = os.statvfs('/')
    block_size = stat[0]
    total_blocks = stat[2]
    free_blocks = stat[3]
    total = total_blocks * block_size
    free = free_blocks * block_size
    used = total - free
    return total, used, free

def get_ram_info():
    free = gc.mem_free()
    total = gc.mem_alloc() + free
    return total, free

def get_scripts_list():
    try:
        scripts = []
        for file in os.listdir("/scripts"):
            if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                stat = os.stat(f"/scripts/{file}")
                scripts.append({"name": file, "size": stat[6]})
        return sorted(scripts, key=lambda x: x["name"])
    except:
        return []

def sanitize_filename(filename):
    filename = filename.replace("..", "").replace("/", "").replace("\\", "").replace("\x00", "")
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")
    filename = ''.join(c for c in filename if c in allowed_chars)
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        filename += ".duck"
    return filename

def delete_script(filename):
    try:
        os.remove(f"/scripts/{filename}")
        return True
    except:
        return False

def rename_script(old_name, new_name):
    try:
        old_name = sanitize_filename(old_name)
        new_name = sanitize_filename(new_name)
        if old_name != new_name:
            os.rename(f"/scripts/{old_name}", f"/scripts/{new_name}")
        return True
    except:
        return False

def save_script(filename, content):
    try:
        if len(content) > MAX_FILE_SIZE:
            return False, f"File too large (max {MAX_FILE_SIZE} bytes)"
        
        _, _, free = get_storage_info()
        if len(content) > free:
            return False, "Not enough storage space"
        
        with open(f"/scripts/{filename}", "w") as f:
            f.write(content)
        return True, "Saved successfully"
    except Exception as e:
        return False, f"Error saving: {str(e)}"

def read_script(filename):
    try:
        with open(f"/scripts/{filename}", "r") as f:
            return f.read()
    except:
        return None

def url_decode(s):
    """Simple URL decoder without urllib"""
    s = s.replace('+', ' ')
    i = 0
    result = []
    while i < len(s):
        if s[i] == '%' and i + 2 < len(s):
            try:
                hex_val = s[i+1:i+3]
                char_code = int(hex_val, 16)
                result.append(chr(char_code))
                i += 3
            except:
                result.append(s[i])
                i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

# ========== HTML TEMPLATES ==========
def html_header(title):
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title} - Ducky Script Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Courier New', monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .stats {{ background: #2d2d2d; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #4ec9b0; }}
        .script-item {{ background: #2d2d2d; margin: 10px 0; padding: 15px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }}
        .script-name {{ font-weight: bold; color: #9cdcfe; word-break: break-all; }}
        .button-group {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        button, .button {{ background: #0e639c; color: white; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer; text-decoration: none; display: inline-block; font-size: 14px; font-family: monospace; }}
        .danger {{ background: #a1260d; }}
        .success {{ background: #6a9955; }}
        textarea {{ width: 100%; height: 400px; background: #252526; color: #d4d4d4; border: 1px solid #3e3e42; padding: 10px; font-family: monospace; margin: 10px 0; }}
        input[type="text"] {{ width: 100%; padding: 10px; margin: 10px 0; background: #3c3c3c; color: #d4d4d4; border: 1px solid #555; }}
        .message {{ padding: 10px; margin: 10px 0; border-radius: 3px; }}
        .error {{ background: #5a1e1e; border-left: 4px solid #f48771; }}
        .success-msg {{ background: #1e3a1e; border-left: 4px solid #6a9955; }}
        .nav-bar {{ background: #2d2d2d; padding: 10px; margin-bottom: 20px; border-radius: 5px; display: flex; justify-content: space-between; }}
    </style>
</head>
<body>
<div class="container">
    <div class="nav-bar">
        <span>[DSM] Ducky Script Manager</span>
        <a href="/" class="button">[Home]</a>
    </div>
"""

def html_footer():
    return "</div></body></html>"

def dashboard():
    total_storage, used_storage, free_storage = get_storage_info()
    total_ram, free_ram = get_ram_info()
    scripts = get_scripts_list()
    
    html = html_header("Dashboard")
    html += f"""
    <div class="stats">
        <h2>System Status</h2>
        <p>[Storage] {used_storage//1024}KB / {total_storage//1024}KB used</p>
        <p>[RAM] {free_ram//1024}KB free / {total_ram//1024}KB total</p>
    </div>
    <div style="margin: 20px 0;">
        <a href="/new" class="button success">[+] Create New Script</a>
    </div>
    <h2>Scripts ({len(scripts)})</h2>
    """
    
    if not scripts:
        html += '<div class="message">No scripts found. Create your first script!</div>'
    else:
        for script in scripts:
            size_kb = script["size"] // 1024
            size_str = f"{size_kb}KB" if size_kb > 0 else f"{script['size']}B"
            encoded_name = script['name'].replace(' ', '%20')
            html += f"""
            <div class="script-item">
                <div><div class="script-name">[File] {script['name']}</div><div>{size_str}</div></div>
                <div class="button-group">
                    <a href="/view?file={encoded_name}" class="button">[View]</a>
                    <a href="/edit?file={encoded_name}" class="button">[Edit]</a>
                    <a href="/rename?file={encoded_name}" class="button">[Rename]</a>
                    <a href="/delete?file={encoded_name}" class="button danger" onclick="return confirm('Delete this script?')">[Delete]</a>
                </div>
            </div>"""
    
    html += html_footer()
    return html

def view_script(filename):
    content = read_script(filename)
    if content is None:
        return error_page("Script not found")
    
    html = html_header(f"View: {filename}")
    html += f"""
    <h2>Viewing: {filename}</h2>
    <div class="stats">
        <p>Size: {len(content)} bytes</p>
        <a href="/edit?file={filename}" class="button">[Edit]</a>
        <a href="/" class="button">[Back]</a>
    </div>
    <textarea readonly>{content}</textarea>
    """
    html += html_footer()
    return html

def edit_script(filename, error=None):
    content = read_script(filename) if filename else ""
    error_html = f'<div class="message error">{error}</div>' if error else ''
    
    html = html_header(f"Edit: {filename}" if filename else "New Script")
    html += f"""
    <h2>{'Edit Script' if filename else 'Create New Script'}</h2>
    {error_html}
    <form method="POST" action="/save">
        <input type="hidden" name="original_name" value="{filename if filename else ''}">
        <input type="text" name="filename" placeholder="Script name (e.g., payload.duck)" value="{filename if filename else ''}" required>
        <textarea name="content" placeholder="Enter Ducky Script here...&#10;&#10;Examples:&#10;DELAY 1000&#10;STRING Hello World&#10;ENTER&#10;GUI r" required>{content}</textarea>
        <div class="button-group">
            <button type="submit" class="success">[Save]</button>
            <a href="/" class="button">[Cancel]</a>
            {f'<a href="/delete?file={filename}" class="button danger" onclick="return confirm(\'Delete this script?\')">[Delete]</a>' if filename else ''}
        </div>
    </form>
    """
    html += html_footer()
    return html

def rename_script_page(filename, error=None):
    error_html = f'<div class="message error">{error}</div>' if error else ''
    html = html_header(f"Rename: {filename}")
    html += f"""
    <h2>Rename Script</h2>
    {error_html}
    <form method="POST" action="/do_rename">
        <input type="hidden" name="old_name" value="{filename}">
        <input type="text" name="new_name" placeholder="New name (e.g., payload.duck)" value="{filename}" required>
        <div class="button-group">
            <button type="submit" class="success">[Rename]</button>
            <a href="/" class="button">[Cancel]</a>
        </div>
    </form>
    """
    html += html_footer()
    return html

def error_page(message):
    html = html_header("Error")
    html += f'<div class="message error">[ERROR] {message}</div>'
    html += f'<a href="/" class="button">[Back to Dashboard]</a>'
    html += html_footer()
    return html

def success_page(message):
    html = html_header("Success")
    html += f'<div class="message success-msg">[SUCCESS] {message}</div>'
    html += f'<meta http-equiv="refresh" content="2;url=/">'
    html += html_footer()
    return html

def parse_query_string(path):
    params = {}
    if '?' in path:
        query = path.split('?')[1]
        parts = query.split('&')
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                params[key] = url_decode(value)
            else:
                params[part] = ''
    return params

def handle_request(client_socket, request):
    try:
        lines = request.split('\r\n')
        if not lines:
            return
        
        request_line = lines[0].split(' ')
        if len(request_line) < 2:
            return
            
        method = request_line[0]
        full_path = request_line[1]
        path = full_path.split('?')[0]
        params = parse_query_string(full_path)
        
        print(f"Request: {method} {full_path}")
        
        if path == "/" or path == "":
            response = dashboard()
            client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
            client_socket.send(response)
        
        elif path == "/view":
            if 'file' in params:
                response = view_script(params['file'])
                client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
            else:
                response = error_page("No file specified")
                client_socket.send("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
        
        elif path == "/edit":
            filename = params.get('file', None)
            response = edit_script(filename)
            client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
            client_socket.send(response)
        
        elif path == "/new":
            response = edit_script(None)
            client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
            client_socket.send(response)
        
        elif path == "/rename":
            if 'file' in params:
                response = rename_script_page(params['file'])
                client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
            else:
                response = error_page("No file specified")
                client_socket.send("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
        
        elif path == "/save" and method == "POST":
            body = request.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in request else ''
            original_name = ""
            filename = ""
            content = ""
            
            if body:
                parts = body.split('&')
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        if key == 'original_name':
                            original_name = url_decode(value)
                        elif key == 'filename':
                            filename = url_decode(value)
                        elif key == 'content':
                            content = url_decode(value)
            
            if filename:
                filename = sanitize_filename(filename)
                success, msg = save_script(filename, content)
                if success:
                    if original_name and original_name != filename:
                        delete_script(original_name)
                    response = success_page(msg)
                else:
                    response = edit_script(filename, msg)
                client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
            else:
                response = error_page("No filename provided")
                client_socket.send("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
        
        elif path == "/delete":
            if 'file' in params:
                delete_script(params['file'])
                response = success_page(f"Deleted {params['file']}")
                client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
            else:
                response = error_page("No file specified")
                client_socket.send("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
        
        elif path == "/do_rename" and method == "POST":
            body = request.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in request else ''
            old_name = ""
            new_name = ""
            
            if body:
                parts = body.split('&')
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        if key == 'old_name':
                            old_name = url_decode(value)
                        elif key == 'new_name':
                            new_name = url_decode(value)
            
            if old_name and new_name:
                old_name = sanitize_filename(old_name)
                new_name = sanitize_filename(new_name)
                if rename_script(old_name, new_name):
                    response = success_page(f"Renamed to {new_name}")
                else:
                    response = error_page("Rename failed")
                client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
            else:
                response = error_page("Invalid names")
                client_socket.send("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
                client_socket.send(response)
        
        else:
            client_socket.send("HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
            client_socket.send("<h1>404 Not Found</h1>")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            client_socket.close()
        except:
            pass
        gc.collect()

def start_server():
    init_storage()
    
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)
    
    while not ap.active():
        time.sleep(0.1)
    
    print("\n" + "="*50)
    print("Ducky Script Manager - Web Server Ready")
    print("="*50)
    print(f"SSID: {AP_SSID}")
    print(f"WiFi Password: {AP_PASSWORD}")
    print(f"Web Interface: http://{ap.ifconfig()[0]}")
    print("="*50 + "\n")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', HTTP_PORT))
    server_socket.listen(1)
    
    print("Server running! Press Ctrl+C to stop.\n")
    
    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            request = client_socket.recv(1024).decode('utf-8', 'ignore')
            if request:
                handle_request(client_socket, request)
            else:
                client_socket.close()
        except KeyboardInterrupt:
            print("\n\nServer stopped by user")
            break
        except Exception as e:
            print(f"Server error: {e}")
            time.sleep(0.1)
            gc.collect()
    
    server_socket.close()
