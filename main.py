import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkTextbox, CTkProgressBar, CTkScrollableFrame, CTkSegmentedButton
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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SysForge(CTk):
    def __init__(self):
        super().__init__()
        
        self.title("SysForge - IT Command Center")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
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
        
        self.configure(fg_color=self.colors['bg_dark'])
        
        self.command_queue = queue.Queue()
        self.is_running = False
        self.current_view = "terminal"
        self.active_category = None
        
        self.setup_ui()
        self.update_clock()
        self.process_queue()
        self.update_system_stats()
        
    def setup_ui(self):
        self.main_container = CTkFrame(self, fg_color=self.colors['bg_dark'], corner_radius=15)
        self.main_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.create_header()
        
        self.content_frame = CTkFrame(self.main_container, fg_color=self.colors['bg_dark'], corner_radius=15)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.create_navigation()
        self.create_main_panel()
        self.create_status_bar()
        
    def create_header(self):
        header = CTkFrame(self.main_container, height=60, fg_color=self.colors['bg_medium'], corner_radius=15)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
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
        
        self.clock_label = CTkLabel(
            header,
            text="",
            font=("Consolas", 14),
            text_color=self.colors['neon_purple']
        )
        self.clock_label.pack(side="right", padx=20)
        
        status_frame = CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", padx=20)
        
        self.status_indicators = {}
        for status in ['CPU', 'RAM', 'DISK']:
            indicator = CTkFrame(status_frame, fg_color=self.colors['bg_light'], width=80, height=30, corner_radius=10)
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
        
    def create_navigation(self):
        self.nav_panel = CTkFrame(self.content_frame, width=220, fg_color=self.colors['bg_medium'], corner_radius=15)
        self.nav_panel.pack(side="left", fill="y", padx=(0, 5))
        self.nav_panel.pack_propagate(False)
        
        CTkLabel(
            self.nav_panel,
            text="CATEGORIES",
            font=("Consolas", 14, "bold"),
            text_color=self.colors['neon_blue']
        ).pack(pady=(20, 10))
        
        self.nav_scroll = CTkScrollableFrame(
            self.nav_panel,
            fg_color="transparent",
            scrollbar_button_color=self.colors['neon_blue'],
            scrollbar_button_hover_color=self.colors['neon_purple']
        )
        self.nav_scroll.pack(fill="both", expand=True, padx=8, pady=5)
        
        self.categories_data = {
            "🌐 NETWORK": {
                "buttons": [
                    ("Show IP Config", self.show_ip_config),
                    ("Flush DNS", self.flush_dns),
                    ("Renew DHCP", self.renew_dhcp),
                    ("Restart DNS Client", self.restart_dns_client),
                    ("Ping Google", self.ping_google),
                    ("Ping Gateway", self.ping_gateway),
                    ("Check Internet", self.check_internet),
                    ("Custom Ping", self.custom_ping),
                    ("Network Reset", self.network_reset),
                ]
            },
            "💻 SYSTEM": {
                "buttons": [
                    ("System Info", self.system_info),
                    ("Disk Usage", self.disk_usage),
                    ("Disk Scan", self.disk_scan),
                    ("Clean Temp Files", self.clean_temp),
                    ("Empty Recycle Bin", self.empty_recycle_bin),
                    ("GPUpdate", self.gpupdate),
                    ("Restart Print Spooler", self.restart_print_spooler),
                ]
            },
            "🔧 MAINTENANCE": {
                "buttons": [
                    ("Full Maintenance", self.full_maintenance),
                    ("Windows Defender Scan", self.defender_scan),
                    ("RAM Cleaner", self.ram_cleaner),
                    ("Startup Optimizer", self.startup_optimizer),
                ]
            }
        }
        
        self.build_navigation()
        
    def build_navigation(self):
        for widget in self.nav_scroll.winfo_children():
            widget.destroy()
        
        for category_name, category_data in self.categories_data.items():
            is_active = (self.active_category == category_name)
            
            cat_btn = CTkButton(
                self.nav_scroll,
                text=category_name,
                command=lambda c=category_name: self.toggle_category(c),
                fg_color=self.colors['neon_blue'] if is_active else self.colors['bg_light'],
                hover_color=self.colors['neon_blue'],
                text_color=self.colors['text_primary'],
                font=("Consolas", 12, "bold"),
                height=42,
                corner_radius=12,
                anchor="w"
            )
            cat_btn.pack(fill="x", pady=2)
            
            if is_active:
                buttons_frame = CTkFrame(self.nav_scroll, fg_color=self.colors['bg_dark'], corner_radius=10)
                
                for btn_text, btn_command in category_data["buttons"]:
                    btn = CTkButton(
                        buttons_frame,
                        text=btn_text,
                        command=btn_command,
                        fg_color="transparent",
                        hover_color=self.colors['neon_purple'],
                        text_color=self.colors['text_secondary'],
                        font=("Consolas", 10),
                        height=34,
                        corner_radius=8,
                        anchor="w"
                    )
                    btn.pack(fill="x", padx=5, pady=1)
                
                buttons_frame.pack(fill="x", pady=(0, 5))
        
    def toggle_category(self, category_name):
        if self.active_category == category_name:
            self.active_category = None
        else:
            self.active_category = category_name
        
        self.build_navigation()
        
    def create_main_panel(self):
        self.main_panel = CTkFrame(self.content_frame, fg_color=self.colors['bg_medium'], corner_radius=15)
        self.main_panel.pack(side="right", fill="both", expand=True)
        
        self.view_selector = CTkSegmentedButton(
            self.main_panel,
            values=["📟 Terminal", "📊 Dashboard"],
            command=self.switch_view,
            fg_color=self.colors['bg_light'],
            selected_color=self.colors['neon_blue'],
            unselected_color=self.colors['bg_light'],
            text_color=self.colors['text_primary'],
            font=("Consolas", 12, "bold"),
            corner_radius=12
        )
        self.view_selector.pack(pady=10, padx=10)
        self.view_selector.set("📟 Terminal")
        
        self.terminal_frame = CTkFrame(self.main_panel, fg_color="transparent")
        self.dashboard_frame = CTkFrame(self.main_panel, fg_color="transparent")
        
        self.create_terminal_view()
        self.create_dashboard_view()
        
        self.terminal_frame.pack(fill="both", expand=True)
        
    def create_terminal_view(self):
        terminal_header = CTkFrame(self.terminal_frame, fg_color=self.colors['bg_light'], height=40, corner_radius=12)
        terminal_header.pack(fill="x", padx=10)
        terminal_header.pack_propagate(False)
        
        CTkLabel(
            terminal_header,
            text="📟 SYSTEM TERMINAL",
            font=("Consolas", 14, "bold"),
            text_color=self.colors['neon_green']
        ).pack(side="left", padx=20)
        
        controls_frame = CTkFrame(terminal_header, fg_color="transparent")
        controls_frame.pack(side="right", padx=10)
        
        for text, cmd, color in [("📋 Copy", self.copy_logs, self.colors['text_primary']), 
                                   ("💾 Save", self.save_logs, self.colors['text_primary']), 
                                   ("🗑️ Clear", self.clear_terminal, self.colors['neon_red'])]:
            CTkButton(
                controls_frame,
                text=text,
                command=cmd,
                width=80,
                height=30,
                fg_color=self.colors['bg_medium'],
                text_color=color,
                font=("Consolas", 10),
                corner_radius=8
            ).pack(side="left", padx=2)
        
        self.terminal = CTkTextbox(
            self.terminal_frame,
            fg_color=self.colors['bg_dark'],
            text_color=self.colors['neon_green'],
            font=("Consolas", 11),
            wrap="word",
            corner_radius=12
        )
        self.terminal.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.terminal.tag_config("success", foreground="#00ff88")
        self.terminal.tag_config("error", foreground="#ff4444")
        self.terminal.tag_config("warning", foreground="#ffaa00")
        self.terminal.tag_config("info", foreground="#00d4ff")
        self.terminal.tag_config("header", foreground="#b44dff")
        
        self.progress_frame = CTkFrame(self.terminal_frame, fg_color="transparent", height=30)
        self.progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.progress_bar = CTkProgressBar(
            self.progress_frame,
            fg_color=self.colors['bg_light'],
            progress_color=self.colors['neon_blue'],
            height=15,
            corner_radius=10
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        self.log_terminal("🚀 SysForge IT Command Center Initialized", "header")
        self.log_terminal("=" * 60, "info")
        self.log_terminal("Ready to execute system commands...", "success")
        self.log_terminal("")
        
    def create_dashboard_view(self):
        dashboard_scroll = CTkScrollableFrame(
            self.dashboard_frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors['neon_blue'],
            scrollbar_button_hover_color=self.colors['neon_purple']
        )
        dashboard_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        stats_grid = CTkFrame(dashboard_scroll, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 10))
        
        self.dashboard_labels = {}
        
        cards = [
            ("💻 System", [
                ("Hostname", socket.gethostname()),
                ("OS", "Windows"),
                ("CPU Cores", str(psutil.cpu_count())),
            ]),
            ("🧠 Memory", [
                ("Total RAM", f"{psutil.virtual_memory().total / (1024**3):.1f} GB"),
                ("Available", f"{psutil.virtual_memory().available / (1024**3):.1f} GB"),
                ("Usage", f"{psutil.virtual_memory().percent}%"),
            ]),
            ("💾 Storage", [
                ("Total Disk", f"{psutil.disk_usage('/').total / (1024**3):.1f} GB"),
                ("Free Space", f"{psutil.disk_usage('/').free / (1024**3):.1f} GB"),
                ("Usage", f"{psutil.disk_usage('/').percent}%"),
            ]),
            ("🌐 Network", [
                ("Internet", "Checking..."),
                ("IP Address", self.get_local_ip()),
                ("Gateway", self.get_default_gateway() or "N/A"),
            ]),
        ]
        
        for card_title, card_items in cards:
            card = CTkFrame(stats_grid, fg_color=self.colors['bg_dark'], corner_radius=15)
            card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            CTkLabel(
                card,
                text=card_title,
                font=("Consolas", 14, "bold"),
                text_color=self.colors['neon_purple']
            ).pack(pady=(10, 5))
            
            for label, value in card_items:
                item_frame = CTkFrame(card, fg_color="transparent")
                item_frame.pack(fill="x", padx=10, pady=2)
                
                CTkLabel(
                    item_frame,
                    text=f"{label}:",
                    font=("Consolas", 10),
                    text_color=self.colors['text_secondary']
                ).pack(side="left")
                
                value_label = CTkLabel(
                    item_frame,
                    text=value,
                    font=("Consolas", 10, "bold"),
                    text_color=self.colors['neon_green']
                )
                value_label.pack(side="right")
                self.dashboard_labels[f"{card_title}_{label}"] = value_label
        
        self.dashboard_output = CTkFrame(dashboard_scroll, fg_color=self.colors['bg_dark'], corner_radius=15)
        self.dashboard_output.pack(fill="both", expand=True)
        
        CTkLabel(
            self.dashboard_output,
            text="📋 COMMAND OUTPUT",
            font=("Consolas", 14, "bold"),
            text_color=self.colors['neon_blue']
        ).pack(pady=(10, 5))
        
        self.dashboard_output_textbox = CTkTextbox(
            self.dashboard_output,
            fg_color=self.colors['bg_medium'],
            text_color=self.colors['neon_green'],
            font=("Consolas", 11),
            wrap="word",
            height=200,
            corner_radius=12
        )
        self.dashboard_output_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.dashboard_output_textbox.tag_config("success", foreground="#00ff88")
        self.dashboard_output_textbox.tag_config("error", foreground="#ff4444")
        self.dashboard_output_textbox.tag_config("warning", foreground="#ffaa00")
        self.dashboard_output_textbox.tag_config("info", foreground="#00d4ff")
        self.dashboard_output_textbox.tag_config("header", foreground="#b44dff")
        
        self.dashboard_output_textbox.insert("end", "Run commands to see output here...\n", "info")
        
        self.update_dashboard_stats()
        
    def update_dashboard_stats(self):
        try:
            self.dashboard_labels["💻 System_Hostname"].configure(text=socket.gethostname())
            self.dashboard_labels["🧠 Memory_Total RAM"].configure(text=f"{psutil.virtual_memory().total / (1024**3):.1f} GB")
            self.dashboard_labels["🧠 Memory_Available"].configure(text=f"{psutil.virtual_memory().available / (1024**3):.1f} GB")
            self.dashboard_labels["🧠 Memory_Usage"].configure(text=f"{psutil.virtual_memory().percent}%")
            self.dashboard_labels["💾 Storage_Total Disk"].configure(text=f"{psutil.disk_usage('/').total / (1024**3):.1f} GB")
            self.dashboard_labels["💾 Storage_Free Space"].configure(text=f"{psutil.disk_usage('/').free / (1024**3):.1f} GB")
            self.dashboard_labels["💾 Storage_Usage"].configure(text=f"{psutil.disk_usage('/').percent}%")
            
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                self.dashboard_labels["🌐 Network_Internet"].configure(text="Connected ✓", text_color=self.colors['neon_green'])
            except:
                self.dashboard_labels["🌐 Network_Internet"].configure(text="Disconnected ✗", text_color=self.colors['neon_red'])
        except:
            pass
        
        self.after(3000, self.update_dashboard_stats)
        
    def switch_view(self, choice):
        self.terminal_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        
        if choice == "📟 Terminal":
            self.terminal_frame.pack(fill="both", expand=True)
            self.current_view = "terminal"
        else:
            self.dashboard_frame.pack(fill="both", expand=True)
            self.current_view = "dashboard"
        
    def create_status_bar(self):
        status_bar = CTkFrame(self.main_container, height=30, fg_color=self.colors['bg_medium'], corner_radius=10)
        status_bar.pack(fill="x", padx=10, pady=(0, 10))
        status_bar.pack_propagate(False)
        
        self.status_label = CTkLabel(
            status_bar,
            text="● Ready | Admin: Checking...",
            font=("Consolas", 10),
            text_color=self.colors['neon_green']
        )
        self.status_label.pack(side="left", padx=20)
        
        if self.is_admin():
            self.status_label.configure(text="● Ready | Admin: ✓")
        else:
            self.status_label.configure(text="● Ready | Admin: ✗ (Limited)")
            
    def log_terminal(self, message, tag=None):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.terminal.insert("end", formatted_message, tag)
        self.terminal.see("end")
        
        if hasattr(self, 'dashboard_output_textbox'):
            self.dashboard_output_textbox.insert("end", formatted_message, tag)
            self.dashboard_output_textbox.see("end")
        
        self.update()
        
    def run_command(self, command, shell=True):
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
        if self.is_running:
            self.log_terminal("⚠️ Another command is already running", "warning")
            return
            
        def worker():
            self.is_running = True
            self.status_label.configure(text=f"⏳ Running: {description}")
            
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
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc.memory_info()
                    except:
                        pass
                        
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
        
    def get_default_gateway(self):
        try:
            gateways = psutil.net_if_addrs()
            for interface, addrs in gateways.items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                        ip_parts = addr.address.split('.')
                        ip_parts[-1] = '1'
                        return '.'.join(ip_parts)
        except:
            pass
        return None
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "N/A"
        
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
        if hasattr(self, 'dashboard_output_textbox'):
            self.dashboard_output_textbox.delete("1.0", "end")
            self.dashboard_output_textbox.insert("end", "Run commands to see output here...\n", "info")
        self.log_terminal("🗑️ Terminal cleared", "info")
        
def main():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        
    app = SysForge()
    app.mainloop()
    
if __name__ == "__main__":
    main()