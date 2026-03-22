import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import asyncio
import threading
import json
import os
import time
import ctypes
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

class TelegramExactScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram ExactTime Scheduler")
        self.root.geometry("480x720")
        self.root.resizable(False, False)
        
        self.cancel_flag = False
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        self.settings_file = "settings.json"
        
        self.create_widgets()
        self.load_settings()
        
    def create_widgets(self):
        mainframe = ttk.Frame(self.root, padding="20 20 20 20")
        mainframe.pack(fill=tk.BOTH, expand=True)

        # 1. API Credentials Frame
        api_frame = ttk.LabelFrame(mainframe, text="1. API Credentials (my.telegram.org)", padding="10 10 10 10")
        api_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(api_frame, text="API ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_id_var = tk.StringVar()
        self.entry_api_id = ttk.Entry(api_frame, textvariable=self.api_id_var, width=30, show="*")
        self.entry_api_id.grid(row=0, column=1, sticky=tk.E, pady=2)

        ttk.Label(api_frame, text="API Hash:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.api_hash_var = tk.StringVar()
        self.entry_api_hash = ttk.Entry(api_frame, textvariable=self.api_hash_var, width=30, show="*")
        self.entry_api_hash.grid(row=1, column=1, sticky=tk.E, pady=2)

        ttk.Label(api_frame, text="Your Phone (+880...):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.phone_var = tk.StringVar()
        self.entry_phone = ttk.Entry(api_frame, textvariable=self.phone_var, width=30, show="*")
        self.entry_phone.grid(row=2, column=1, sticky=tk.E, pady=2)

        self.show_cred_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(api_frame, text="Show Credentials", variable=self.show_cred_var, command=self.toggle_credentials).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5,0))

        # 2. Target Details Frame
        target_frame = ttk.LabelFrame(mainframe, text="2. Message Details", padding="10 10 10 10")
        target_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        ttk.Label(target_frame, text="Target (@username or Phone):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.target_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.target_var, width=28).grid(row=0, column=1, sticky=tk.E, pady=2)

        ttk.Label(target_frame, text="Message:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.msg_text = tk.Text(target_frame, width=28, height=6, font=("Segoe UI", 10))
        self.msg_text.grid(row=1, column=1, sticky=tk.E, pady=5)

        # 3. Schedule Time Frame
        time_frame = ttk.LabelFrame(mainframe, text="3. Target Time (Exact)", padding="10 10 10 10")
        time_frame.pack(fill=tk.X, pady=(0, 15))

        time_inner = ttk.Frame(time_frame)
        time_inner.pack(pady=5)

        self.hr_var = tk.StringVar(value="02")
        ttk.Spinbox(time_inner, from_=1, to=12, textvariable=self.hr_var, width=3, format="%02.0f").pack(side=tk.LEFT, padx=2)
        ttk.Label(time_inner, text=":").pack(side=tk.LEFT)
        
        self.mn_var = tk.StringVar(value="00")
        ttk.Spinbox(time_inner, from_=0, to=59, textvariable=self.mn_var, width=3, format="%02.0f").pack(side=tk.LEFT, padx=2)
        ttk.Label(time_inner, text=":").pack(side=tk.LEFT)

        self.sc_var = tk.StringVar(value="00")
        ttk.Spinbox(time_inner, from_=0, to=59, textvariable=self.sc_var, width=3, format="%02.0f").pack(side=tk.LEFT, padx=2)
        ttk.Label(time_inner, text=".").pack(side=tk.LEFT)

        self.ms_var = tk.StringVar(value="000")
        ttk.Spinbox(time_inner, from_=0, to=999, textvariable=self.ms_var, width=4, format="%03.0f").pack(side=tk.LEFT, padx=2)
        
        self.ampm_var = tk.StringVar(value="PM")
        ttk.Combobox(time_inner, textvariable=self.ampm_var, values=["AM", "PM"], width=4, state="readonly").pack(side=tk.LEFT, padx=10)

        # 4. Action and Status
        btn_frame = ttk.Frame(mainframe)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Login & Start Schedule", command=self.start_scheduling)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)

        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_scheduling, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=5)

        self.status_label = ttk.Label(mainframe, text="Status: Ready", font=("Segoe UI", 10, "bold"), foreground="blue")
        self.status_label.pack(pady=5)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    self.api_id_var.set(data.get("api_id", ""))
                    self.api_hash_var.set(data.get("api_hash", ""))
                    self.phone_var.set(data.get("phone", ""))
                    self.target_var.set(data.get("target", ""))
                    msg = data.get("msg", "")
                    if msg:
                        self.msg_text.insert("1.0", msg)
            except Exception as e:
                print("Error loading settings:", e)

    def save_settings(self, api_id, api_hash, phone, target, msg):
        try:
            data = {
                "api_id": api_id,
                "api_hash": api_hash,
                "phone": phone,
                "target": target,
                "msg": msg
            }
            with open(self.settings_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print("Error saving settings:", e)

    def update_status(self, text, color="blue"):
        self.root.after(0, lambda: self.status_label.config(text=f"Status: {text}", foreground=color))

    def toggle_credentials(self):
        char = "" if self.show_cred_var.get() else "*"
        self.entry_api_id.config(show=char)
        self.entry_api_hash.config(show=char)
        self.entry_phone.config(show=char)

    def cancel_scheduling(self):
        self.cancel_flag = True
        self.update_status("Schedule Cancelled", "red")
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)

    def start_scheduling(self):
        # Gather info
        api_id = self.api_id_var.get().strip()
        api_hash = self.api_hash_var.get().strip()
        phone = self.phone_var.get().strip()
        target = self.target_var.get().strip()
        msg = self.msg_text.get("1.0", tk.END).strip()
        
        hr = int(self.hr_var.get())
        mn = int(self.mn_var.get())
        sc = int(self.sc_var.get())
        ms = int(self.ms_var.get())
        period = self.ampm_var.get()

        if not api_id.isdigit() or not api_hash or not phone or not target or not msg:
            messagebox.showerror("Validation Error", "Please fill in all the fields correctly.")
            return

        # Save settings for next time
        self.save_settings(api_id, api_hash, phone, target, msg)

        # Time Conversion (12h to 24h)
        if period == "PM" and hr != 12:
            hr += 12
        elif period == "AM" and hr == 12:
            hr = 0

        self.cancel_flag = False
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        
        # Run in a background thread to keep GUI responsive
        threading.Thread(
            target=self.run_async_loop, 
            args=(int(api_id), api_hash, phone, target, msg, hr, mn, sc, ms),
            daemon=True
        ).start()

    def run_async_loop(self, api_id, api_hash, phone, target, msg, hr, mn, sc, ms):
        try:
            asyncio.run(self.async_sender(api_id, api_hash, phone, target, msg, hr, mn, sc, ms))
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
            messagebox.showerror("Error", str(e))
        finally:
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.cancel_btn.config(state=tk.DISABLED))

    async def async_sender(self, api_id, api_hash, phone, target, msg, hr, mn, sc, ms):
        # === WINDOWS: Set timer resolution to 1ms for accurate sleep ===
        winmm = None
        try:
            winmm = ctypes.windll.winmm
            winmm.timeBeginPeriod(1)
        except Exception:
            pass  # Non-Windows or unavailable, continue anyway

        try:
            await self._do_send(api_id, api_hash, phone, target, msg, hr, mn, sc, ms)
        finally:
            # Always restore timer resolution
            if winmm:
                try:
                    winmm.timeEndPeriod(1)
                except Exception:
                    pass

    async def _do_send(self, api_id, api_hash, phone, target, msg, hr, mn, sc, ms):
        # 1. Initialize Telegram Client
        session_name = 'session_files/' + phone.replace('+', '')
        client = TelegramClient(session_name, api_id, api_hash)
        
        self.update_status("Connecting to Telegram...", "blue")
        await client.connect()

        # 2. Handle Login (OTP and Password via GUI dialogs)
        if not await client.is_user_authorized():
            self.update_status("Sending OTP Request...", "orange")
            await client.send_code_request(phone)
            
            code = await self.ask_gui_async("OTP Required", f"Enter the 5-digit Telegram code sent to {phone}:")
            if not code:
                self.update_status("Login Cancelled (No OTP)", "red")
                return
                
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                pwd = await self.ask_gui_async("2FA Password Required", "Your account has 2-Step Verification. Enter password:")
                if not pwd:
                    self.update_status("Login Cancelled (No Password)", "red")
                    return
                await client.sign_in(password=pwd)

        self.update_status("Login Successful! Preparing...", "green")

        # 3. PRE-RESOLVE target entity (avoids extra API call at send time)
        self.update_status("Resolving target entity...", "blue")
        try:
            entity = await client.get_entity(target)
        except Exception as e:
            self.update_status(f"Error: Could not find target '{target}'", "red")
            messagebox.showerror("Error", f"Could not find target '{target}': {e}")
            await client.disconnect()
            return

        # 4. SYNC WITH TELEGRAM SERVER CLOCK
        # Your PC clock may be ahead/behind Telegram's server clock.
        # We measure the exact offset to fire at the correct SERVER time.
        self.update_status("Syncing with Telegram server clock...", "blue")
        
        offsets = []
        for i in range(3):
            local_before = datetime.utcnow()
            test_msg = await client.send_message('me', f'⏱ clock sync {i+1}/3')
            local_after = datetime.utcnow()
            
            server_time = test_msg.date.replace(tzinfo=None)  # UTC, no timezone
            local_mid = local_before + (local_after - local_before) / 2  # midpoint estimate
            
            offset = (server_time - local_mid).total_seconds()
            offsets.append(offset)
            
            await test_msg.delete()
            if i < 2:
                await asyncio.sleep(0.3)
        
        # Average offset: positive = server is AHEAD of local, negative = server is BEHIND
        clock_offset = sum(offsets) / len(offsets)
        offset_ms = int(clock_offset * 1000)
        
        if clock_offset > 0:
            self.update_status(f"Server is {abs(offset_ms)}ms AHEAD of your PC", "blue")
        else:
            self.update_status(f"Server is {abs(offset_ms)}ms BEHIND your PC (will add {abs(offset_ms)}ms delay)", "blue")
        await asyncio.sleep(1.5)  # Let user see the info

        # 5. Time Calculation Logic (adjusted for server clock)
        now = datetime.now()
        target_time = now.replace(hour=hr, minute=mn, second=sc, microsecond=ms * 1000)
        
        if target_time <= now:
            target_time += timedelta(days=1)

        # ADJUST for clock offset: if local clock is ahead, we need to wait LONGER
        # target_time is in LOCAL time. We add the negative offset to make it later.
        adjusted_target = target_time - timedelta(seconds=clock_offset)
        
        time_str = target_time.strftime('%I:%M:%S') + f".{ms:03d} " + target_time.strftime('%p')
        adj_str = adjusted_target.strftime('%H:%M:%S.%f')[:-3]
        wait_msg = f"Target: {time_str} (server-adjusted fire: {adj_str}, offset: {offset_ms}ms)"
        self.update_status(wait_msg, "purple")

        # 6. HIGH-PRECISION WAITING LOOP using perf_counter
        # Use adjusted_target (synced to Telegram server clock), NOT raw target_time
        anchor_real = datetime.now()
        anchor_perf = time.perf_counter()
        target_offset = (adjusted_target - anchor_real).total_seconds()
        fire_perf = anchor_perf + target_offset

        while True:
            if self.cancel_flag:
                await client.disconnect()
                return

            now_perf = time.perf_counter()
            diff = fire_perf - now_perf
            
            if diff <= 0:
                break
                
            if diff > 2.0:
                # Coarse sleep, wake up 1 second early
                await asyncio.sleep(diff - 1.0)
            elif diff > 0.1:
                # Fine sleep, 5ms intervals
                await asyncio.sleep(0.005)
            elif diff > 0.001:
                # Very fine: 0.5ms sleep
                await asyncio.sleep(0.0005)
            # else: tight spin-wait for final 1ms (no sleep, max precision)

        # === STRICT SAFETY GATE ===
        # Verify with REAL system clock against server-adjusted time.
        while datetime.now() < adjusted_target:
            pass  # ultra-tight spin on real clock

        # 7. FIRE MESSAGE
        fire_actual = datetime.now()
        self.update_status("Firing message to server...", "orange")
        
        try:
            # Use pre-resolved entity for fastest send
            await client.send_message(entity, msg)
            
            delivered_time = datetime.now()
            deliver_ms = int((delivered_time - fire_actual).total_seconds() * 1000)
            
            result_msg = (
                f"✅ Done!\n"
                f"Fire time:     {fire_actual.strftime('%H:%M:%S.%f')[:-3]}\n"
                f"Delivered at:  {delivered_time.strftime('%H:%M:%S.%f')[:-3]}\n"
                f"Network took:  {deliver_ms}ms\n"
                f"Target was:    {target_time.strftime('%H:%M:%S.%f')[:-3]}"
            )
            self.update_status(f"Sent! Fired: {fire_actual.strftime('%H:%M:%S.%f')[:-3]} | Delivered: {delivered_time.strftime('%H:%M:%S.%f')[:-3]}", "green")
            messagebox.showinfo("Success", result_msg)
        except Exception as e:
            self.update_status(f"Error sending: {str(e)}", "red")
            messagebox.showerror("Error", f"Failed to send message:\n{str(e)}")
        finally:
            await client.disconnect()


    async def ask_gui_async(self, title, prompt):
        """Helper to pause the async loop and ask for input using Tkinter main thread"""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        
        def ask_in_main_thread():
            # This runs on GUI thread
            res = simpledialog.askstring(title, prompt, parent=self.root)
            loop.call_soon_threadsafe(future.set_result, res)
            
        self.root.after(0, ask_in_main_thread)
        return await future

if __name__ == "__main__":
    # Create session folder if it doesn't exist
    if not os.path.exists("session_files"):
        os.makedirs("session_files")

    root = tk.Tk()
    app = TelegramExactScheduler(root)
    root.mainloop()
