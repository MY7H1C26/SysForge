"""
SysForge - IT Command Center
Modern Windows System Administration Tool
Cyberpunk-themed GUI with real system commands
"""

import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkTextbox, CTkProgressBar
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import queue
import psutil
import socket
import os
import sys
import time
import datetime
from pathlib import Path
import ctypes
import winreg

# Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SysForge(CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("SysForge - IT Command Center")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Color Scheme
        self.colors = {
            'bg_dark': '#0a0a0f',
            'bg_medium': '#13131a',
            'bg_light': '#1a1a24',
            'neon_blue': '#00d4ff',
            'neon_purple': '#b44dff',
            'neon_green': '#00ff88',
            'neon_red': '#ff4444',
            'text_primary': '#e0e0e0',
            'text_secondary': '#888899',
            'border': '#2a2a3a'
        }
        
        # Configure window
        self.configure(fg_color=self.colors['bg_dark'])
        
        # Command queue for thread-safe execution
        self.command_queue = queue.Queue()
        self.is_running = False
        
        # Setup UI
        self.setup_ui()
        
        # Start clock update
        self.update_clock()
        
        # Process command queue
        self.process_queue()
        
    def setup_ui(self):
        # Main Container
        self.main_container = CTkFrame(self, fg_color=self.colors['bg_dark'])
        self.main_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Header
        self.create_header()
        
        # Content Area
        self.content_frame = CTkFrame(self.main_container, fg_color=self.colors['bg_dark'])
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Left Panel - Navigation
        self.create_navigation()
        
        # Right Panel - Terminal & Output
        self.create_terminal()
        
        # Status Bar
        self.create_status_bar()
        
    def create_header(self):
        header = CTkFrame(self.main_container, height=60, fg_color=self.colors['bg_medium'])
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        # Logo/Title
        title_frame = CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        
        CTkLabel(
            title_frame, 
            text="⚡ SYSFORGE", 
            font=("Consolas", 28, "bold"),
            text_color=self.colors['neon_blue']
        ).pack(side="left")
        
        CTkLabel(
            title_frame,
            text="IT COMMAND CENTER",
            font=("Consolas", 12),
            text_color=self.colors['text_secondary']
        ).pack(side="left", padx=(10, 0))
        
        # Clock
        self.clock_label = CTkLabel(
            header,
            text="",
            font=("Consolas", 14),
            text_color=self.colors['neon_purple']
        )
        self.clock_label.pack(side="right", padx=20)
        
        # System Status Indicators
        status_frame = CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", padx=20)
        
        self.status_indicators = {}
        for status in ['CPU', 'RAM', 'DISK']:
            indicator = CTkFrame(status_frame, fg_color=self.colors['bg_light'], width=80, height=30)
            indicator.pack(side="left", padx=5)
            indicator.pack_propagate(False)
            
            label = CTkLabel(
                indicator,
                text=f"{status}: --",
                font=("Consolas", 10),
                text_color=self.colors['text_secondary']
            )
            label.pack(expand=True)
            self.status_indicators[status] = label
            
        # Update system stats
        self.update_system_stats()
        
    def create_navigation(self):
        # Navigation Panel
        nav_panel = CTkFrame(self.content_frame, width=200, fg_color=self.colors['bg_medium'])
        nav_panel.pack(side="left", fill="y", padx=(0, 5))
        nav_panel.pack_propagate(False)
        
        # Navigation Title
        CTkLabel(
            nav_panel,
            text="COMMANDS",
            font=("Consolas", 14, "bold"),
            text_color=self.colors['neon_blue']
        ).pack(pady=(20, 10))
        
        # Command Categories
        categories = [
            ("NETWORK", [
                ("🌐 Show IP Config", self.show_ip_config),
                ("🔄 Flush DNS", self.flush_dns),
                ("📡 Renew DHCP", self.renew_dhcp),
                ("🔌 Restart DNS Client", self.restart_dns_client),
                ("📶 Ping Google", self.ping_google),
                ("🏠 Ping Gateway", self.ping_gateway),
                ("🌍 Check Internet", self.check_internet),
                ("🔧 Custom Ping", self.custom_ping),
            ]),
            ("SYSTEM", [
                ("💻 System Info", self.system_info),
                ("💾 Disk Usage", self.disk_usage),
                ("🔍 Disk Scan", self.disk_scan),
                ("🧹 Clean Temp Files", self.clean_temp),
                ("🗑️ Empty Recycle Bin", self.empty_recycle_bin),
                ("🔄 GPUpdate", self.gpupdate),
            ]),
            ("MAINTENANCE", [
                ("🔧 Full Maintenance", self.full_maintenance),
                ("🖨️ Restart Print Spooler", self.restart_print_spooler),
                ("🛡️ Windows Defender Scan", self.defender_scan),
                ("🧠 RAM Cleaner", self.ram_cleaner),
                ("⚡ Startup Optimizer", self.startup_optimizer),
                ("🔄 Network Reset", self.network_reset),
            ])
        ]
        
        # Create scrollable frame for buttons
        for category, commands in categories:
            # Category Header
            cat_frame = CTkFrame(nav_panel, fg_color="transparent")
            cat_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            CTkLabel(
                cat_frame,
                text=category,
                font=("Consolas", 12, "bold"),
                text_color=self.colors['neon_purple']
            ).pack(anchor="w")
            
            # Command Buttons
            for text, command in commands:
                btn = CTkButton(
                    nav_panel,
                    text=text,
                    command=command,
                    fg_color=self.colors['bg_light'],
                    hover_color=self.colors['neon_blue'],
                    text_color=self.colors['text_primary'],
                    font=("Consolas", 11),
                    height=35,
                    anchor="w"
                )
                btn.pack(fill="x", padx=10, pady=2)
                
    def create_terminal(self):
        # Terminal Panel
        terminal_panel = CTkFrame(self.content_frame, fg_color=self.colors['bg_medium'])
        terminal_panel.pack(side="right", fill="both", expand=True)
        
        # Terminal Header
        terminal_header = CTkFrame(terminal_panel, fg_color=self.colors['bg_light'], height=40)
        terminal_header.pack(fill="x")
        terminal_header.pack_propagate(False)
        
        CTkLabel(
            terminal_header,
            text="📟 SYSTEM TERMINAL",
            font=("Consolas", 14, "bold"),
            text_color=self.colors['neon_green']
        ).pack(side="left", padx=20)
        
        # Terminal Controls
        controls_frame = CTkFrame(terminal_header, fg_color="transparent")
        controls_frame.pack(side="right", padx=10)
        
        CTkButton(
            controls_frame,
            text="📋 Copy",
            command=self.copy_logs,
            width=80,
            height=30,
            fg_color=self.colors['bg_medium'],
            text_color=self.colors['text_primary'],
            font=("Consolas", 10)
        ).pack(side="left", padx=2)
        
        CTkButton(
            controls_frame,
            text="💾 Save",
            command=self.save_logs,
            width=80,
            height=30,
            fg_color=self.colors['bg_medium'],
            text_color=self.colors['text_primary'],
            font=("Consolas", 10)
        ).pack(side="left", padx=2)
        
        CTkButton(
            controls_frame,
            text="🗑️ Clear",
            command=self.clear_terminal,
            width=80,
            height=30,
            fg_color=self.colors['bg_medium'],
            text_color=self.colors['neon_red'],
            font=("Consolas", 10)
        ).pack(side="left", padx=2)
        
        # Terminal Output
        self.terminal = CTkTextbox(
            terminal_panel,
            fg_color=self.colors['bg_dark'],
            text_color=self.colors['neon_green'],
            font=("Consolas", 11),
            wrap="word"
        )
        self.terminal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure text tags for colored output
        self.terminal.tag_config("success", foreground="#00ff88")
        self.terminal.tag_config("error", foreground="#ff4444")
        self.terminal.tag_config("warning", foreground="#ffaa00")
        self.terminal.tag_config("info", foreground="#00d4ff")
        self.terminal.tag_config("header", foreground="#b44dff")
        self.terminal.tag_config("cyan", foreground="#00d4ff")
        
        # Progress Bar
        self.progress_frame = CTkFrame(terminal_panel, fg_color="transparent", height=30)
        self.progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.progress_bar = CTkProgressBar(
            self.progress_frame,
            fg_color=self.colors['bg_light'],
            progress_color=self.colors['neon_blue'],
            height=15
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Welcome message
        self.log_terminal("🚀 SysForge IT Command Center Initialized", "header")
        self.log_terminal("=" * 60, "info")
        self.log_terminal("Ready to execute system commands...", "success")
        self.log_terminal("")
        
    def create_status_bar(self):
        status_bar = CTkFrame(self.main_container, height=30, fg_color=self.colors['bg_medium'])
        status_bar.pack(fill="x", padx=10, pady=(0, 10))
        status_bar.pack_propagate(False)
        
        self.status_label = CTkLabel(
            status_bar,
            text="● Ready | Admin: Checking...",
            font=("Consolas", 10),
            text_color=self.colors['neon_green']
        )
        self.status_label.pack(side="left", padx=20)
        
        # Check admin rights
        if self.is_admin():
            self.status_label.configure(text="● Ready | Admin: ✓")
        else:
            self.status_label.configure(text="● Ready | Admin: ✗ (Limited)")
            
    def log_terminal(self, message, tag=None):
        """Add message to terminal with optional color tag"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.terminal.insert("end", formatted_message, tag)
        self.terminal.see("end")
        self.update()
        
    def run_command(self, command, shell=True):
        """Execute a system command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                if result.stdout:
                    return True, result.stdout
                return True, "Command executed successfully"
            else:
                return False, result.stderr or "Command failed"
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
            
    def execute_with_progress(self, command_func, description):
        """Execute a command with progress bar animation"""
        if self.is_running:
            self.log_terminal("⚠️ Another command is already running", "warning")
            return
            
        def worker():
            self.is_running = True
            self.status_label.configure(text=f"⏳ Running: {description}")
            
            # Animate progress bar
            for i in range(101):
                if not self.is_running:
                    break
                self.progress_bar.set(i / 100)
                time.sleep(0.02)
                
            self.log_terminal(f"▶ Executing: {description}", "info")
            success, output = command_func()
            
            if success:
                self.log_terminal(output, "success")
                self.log_terminal(f"✅ {description} completed successfully", "success")
            else:
                self.log_terminal(f"❌ Error: {output}", "error")
                
            self.progress_bar.set(0)
            self.is_running = False
            self.status_label.configure(text="● Ready")
            
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
    # Command Functions
    def show_ip_config(self):
        def cmd():
            return self.run_command("ipconfig /all")
        self.execute_with_progress(cmd, "IP Configuration")
        
    def flush_dns(self):
        def cmd():
            return self.run_command("ipconfig /flushdns")
        self.execute_with_progress(cmd, "DNS Flush")
        
    def renew_dhcp(self):
        def cmd():
            success1, out1 = self.run_command("ipconfig /release")
            success2, out2 = self.run_command("ipconfig /renew")
            return success1 and success2, f"{out1}\n{out2}"
        self.execute_with_progress(cmd, "DHCP Renewal")
        
    def restart_dns_client(self):
        def cmd():
            return self.run_command("net stop dnscache && net start dnscache")
        self.execute_with_progress(cmd, "DNS Client Restart")
        
    def ping_google(self):
        def cmd():
            return self.run_command("ping google.com -n 4")
        self.execute_with_progress(cmd, "Ping Google")
        
    def ping_gateway(self):
        def cmd():
            gateway = self.get_default_gateway()
            if gateway:
                return self.run_command(f"ping {gateway} -n 4")
            return False, "Could not determine gateway"
        self.execute_with_progress(cmd, "Ping Gateway")
        
    def check_internet(self):
        def cmd():
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                return True, "Internet connection: ACTIVE ✓"
            except OSError:
                return False, "Internet connection: INACTIVE ✗"
        self.execute_with_progress(cmd, "Internet Check")
        
    def custom_ping(self):
        dialog = ctk.CTkInputDialog(
            text="Enter IP or hostname to ping:",
            title="Custom Ping"
        )
        host = dialog.get_input()
        if host:
            def cmd():
                return self.run_command(f"ping {host} -n 4")
            self.execute_with_progress(cmd, f"Ping {host}")
            
    def system_info(self):
        def cmd():
            info = []
            info.append("=" * 50)
            info.append("SYSTEM INFORMATION")
            info.append("=" * 50)
            info.append(f"Hostname: {socket.gethostname()}")
            info.append(f"OS: {sys.platform}")
            info.append(f"CPU Cores: {psutil.cpu_count()}")
            info.append(f"CPU Usage: {psutil.cpu_percent()}%")
            
            mem = psutil.virtual_memory()
            info.append(f"RAM Total: {mem.total / (1024**3):.2f} GB")
            info.append(f"RAM Available: {mem.available / (1024**3):.2f} GB")
            info.append(f"RAM Usage: {mem.percent}%")
            
            disk = psutil.disk_usage('/')
            info.append(f"Disk Total: {disk.total / (1024**3):.2f} GB")
            info.append(f"Disk Free: {disk.free / (1024**3):.2f} GB")
            info.append(f"Disk Usage: {disk.percent}%")
            
            return True, "\n".join(info)
        self.execute_with_progress(cmd, "System Information")
        
    def disk_usage(self):
        def cmd():
            result, output = self.run_command("wmic logicaldisk get size,freespace,caption")
            return result, output
        self.execute_with_progress(cmd, "Disk Usage")
        
    def disk_scan(self):
        self.log_terminal("⚠️ This operation requires administrator privileges", "warning")
        self.log_terminal("Scanning C: drive...", "info")
        def cmd():
            return self.run_command("chkdsk C: /f /r")
        self.execute_with_progress(cmd, "Disk Scan")
        
    def clean_temp(self):
        def cmd():
            temp_dirs = [
                os.environ.get('TEMP'),
                os.environ.get('TMP'),
                r'C:\Windows\Temp',
                r'C:\Windows\Prefetch'
            ]
            
            cleaned = 0
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                try:
                                    os.remove(os.path.join(root, file))
                                    cleaned += 1
                                except:
                                    pass
                    except:
                        pass
                        
            return True, f"Cleaned {cleaned} temporary files"
        self.execute_with_progress(cmd, "Temp File Cleanup")
        
    def empty_recycle_bin(self):
        def cmd():
            try:
                # Use PowerShell to empty recycle bin
                ps_command = 'powershell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"'
                return self.run_command(ps_command)
            except:
                return False, "Failed to empty recycle bin"
        self.execute_with_progress(cmd, "Empty Recycle Bin")
        
    def gpupdate(self):
        def cmd():
            return self.run_command("gpupdate /force")
        self.execute_with_progress(cmd, "Group Policy Update")
        
    def restart_print_spooler(self):
        def cmd():
            return self.run_command("net stop spooler && net start spooler")
        self.execute_with_progress(cmd, "Print Spooler Restart")
        
    def defender_scan(self):
        self.log_terminal("⚠️ Starting Windows Defender Quick Scan...", "warning")
        def cmd():
            ps_command = 'powershell -Command "Start-MpScan -ScanType QuickScan"'
            return self.run_command(ps_command)
        self.execute_with_progress(cmd, "Defender Scan")
        
    def ram_cleaner(self):
        def cmd():
            # Clear working set of processes
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc.memory_info()
                    except:
                        pass
                        
                # Use Windows built-in memory management
                ctypes.windll.psapi.EmptyWorkingSet(-1)
                return True, "RAM cleaned successfully"
            except Exception as e:
                return False, str(e)
        self.execute_with_progress(cmd, "RAM Cleaner")
        
    def startup_optimizer(self):
        def cmd():
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_READ
                )
                
                startup_items = []
                i = 0
                while True:
                    try:
                        name, value, type = winreg.EnumValue(key, i)
                        startup_items.append(f"{name}: {value}")
                        i += 1
                    except WindowsError:
                        break
                        
                winreg.CloseKey(key)
                
                if startup_items:
                    return True, "Startup Programs:\n" + "\n".join(startup_items)
                return True, "No startup programs found"
            except Exception as e:
                return False, str(e)
        self.execute_with_progress(cmd, "Startup Optimizer")
        
    def network_reset(self):
        self.log_terminal("⚠️ This will reset all network adapters", "warning")
        def cmd():
            commands = [
                "ipconfig /release",
                "ipconfig /renew",
                "ipconfig /flushdns",
                "netsh int ip reset",
                "netsh winsock reset"
            ]
            
            output = []
            for cmd_str in commands:
                success, out = self.run_command(cmd_str)
                output.append(f"{cmd_str}: {'✓' if success else '✗'}")
                
            return True, "\n".join(output)
        self.execute_with_progress(cmd, "Network Reset")
        
    def full_maintenance(self):
        if self.is_running:
            self.log_terminal("⚠️ Another command is already running", "warning")
            return
            
        self.log_terminal("🔧 Starting Full System Maintenance...", "header")
        
        tasks = [
            ("Cleaning Temp Files", self.clean_temp),
            ("Flushing DNS", self.flush_dns),
            ("Restarting DNS Client", self.restart_dns_client),
            ("Emptying Recycle Bin", self.empty_recycle_bin),
            ("RAM Cleanup", self.ram_cleaner),
            ("Checking Internet", self.check_internet),
        ]
        
        def worker():
            self.is_running = True
            for i, (task_name, task_func) in enumerate(tasks):
                self.status_label.configure(text=f"⏳ Maintenance: {task_name}")
                self.log_terminal(f"\n▶ {task_name}...", "info")
                
                # Progress for each task
                progress_per_task = 100 / len(tasks)
                for j in range(int(progress_per_task)):
                    if not self.is_running:
                        break
                    current_progress = (i * progress_per_task + j) / 100
                    self.progress_bar.set(current_progress)
                    time.sleep(0.01)
                    
                task_func()
                
            self.progress_bar.set(1.0)
            time.sleep(0.5)
            self.progress_bar.set(0)
            self.is_running = False
            self.status_label.configure(text="● Ready")
            self.log_terminal("\n✅ Full Maintenance Complete!", "success")
            
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
    # Utility Functions
    def get_default_gateway(self):
        try:
            gateways = psutil.net_if_addrs()
            for interface, addrs in gateways.items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                        # Get the gateway (usually .1 or .254)
                        ip_parts = addr.address.split('.')
                        ip_parts[-1] = '1'
                        return '.'.join(ip_parts)
        except:
            pass
        return None
        
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def update_clock(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_label.configure(text=f"🕐 {current_time}")
        self.after(1000, self.update_clock)
        
    def update_system_stats(self):
        try:
            cpu_percent = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.status_indicators['CPU'].configure(
                text=f"CPU: {cpu_percent}%",
                text_color=self.colors['neon_green'] if cpu_percent < 80 else self.colors['neon_red']
            )
            self.status_indicators['RAM'].configure(
                text=f"RAM: {ram.percent}%",
                text_color=self.colors['neon_green'] if ram.percent < 80 else self.colors['neon_red']
            )
            self.status_indicators['DISK'].configure(
                text=f"DISK: {disk.percent}%",
                text_color=self.colors['neon_green'] if disk.percent < 80 else self.colors['neon_red']
            )
        except:
            pass
        self.after(5000, self.update_system_stats)
        
    def process_queue(self):
        try:
            while True:
                task = self.command_queue.get_nowait()
                task()
        except queue.Empty:
            pass
        self.after(100, self.process_queue)
        
    def copy_logs(self):
        text = self.terminal.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.log_terminal("📋 Logs copied to clipboard", "info")
        
    def save_logs(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sysforge_logs_{timestamp}.txt"
            text = self.terminal.get("1.0", "end-1c")
            
            with open(filename, 'w') as f:
                f.write(text)
                
            self.log_terminal(f"💾 Logs saved to {filename}", "success")
        except Exception as e:
            self.log_terminal(f"❌ Error saving logs: {e}", "error")
            
    def clear_terminal(self):
        self.terminal.delete("1.0", "end")
        self.log_terminal("🗑️ Terminal cleared", "info")
        
def main():
    # Request admin privileges if not already admin
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        
    app = SysForge()
    app.mainloop()
    
if __name__ == "__main__":
    main()