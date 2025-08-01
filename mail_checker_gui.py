#!/usr/bin/env python3
"""
Mail Access Checker GUI - Grafiskt gränssnitt för email verifiering
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from mail_access_checker import MailAccessChecker, EmailCheckResult
import queue
import time
from typing import List

class MailCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mail Access Checker")
        self.root.geometry("800x600")
        
        # Mail checker instans
        self.checker = MailAccessChecker()
        
        # Queue för thread communication
        self.result_queue = queue.Queue()
        
        self.setup_ui()
        
        # Starta polling för results
        self.root.after(100, self.check_queue)
    
    def setup_ui(self):
        # Huvudfram
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfigurera grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Single email check
        ttk.Label(main_frame, text="Kontrollera enskild email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        email_frame = ttk.Frame(main_frame)
        email_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        email_frame.grid_columnconfigure(0, weight=1)
        
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(email_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.check_button = ttk.Button(email_frame, text="Kontrollera", command=self.check_single_email)
        self.check_button.grid(row=0, column=1)
        
        # Bulk email check
        ttk.Label(main_frame, text="Bulk kontroll:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        bulk_frame = ttk.Frame(main_frame)
        bulk_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.load_file_button = ttk.Button(bulk_frame, text="Ladda fil", command=self.load_email_file)
        self.load_file_button.grid(row=0, column=0, padx=(0, 5))
        
        self.bulk_check_button = ttk.Button(bulk_frame, text="Kontrollera alla", command=self.check_bulk_emails, state='disabled')
        self.bulk_check_button.grid(row=0, column=1)
        
        self.file_label = ttk.Label(bulk_frame, text="Ingen fil vald")
        self.file_label.grid(row=0, column=2, padx=(10, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Redo")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Resultat", padding="5")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Export buttons
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.export_csv_button = ttk.Button(export_frame, text="Exportera CSV", command=lambda: self.export_results('csv'), state='disabled')
        self.export_csv_button.grid(row=0, column=0, padx=(0, 5))
        
        self.export_json_button = ttk.Button(export_frame, text="Exportera JSON", command=lambda: self.export_results('json'), state='disabled')
        self.export_json_button.grid(row=0, column=1)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Inställningar", padding="5")
        settings_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(settings_frame, text="Timeout (s):").grid(row=0, column=0, padx=(0, 5))
        self.timeout_var = tk.IntVar(value=10)
        timeout_spin = ttk.Spinbox(settings_frame, from_=5, to=60, textvariable=self.timeout_var, width=10)
        timeout_spin.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(settings_frame, text="Workers:").grid(row=0, column=2, padx=(0, 5))
        self.workers_var = tk.IntVar(value=5)
        workers_spin = ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.workers_var, width=10)
        workers_spin.grid(row=0, column=3)
        
        # Bind Enter key to check email
        self.email_entry.bind('<Return>', lambda e: self.check_single_email())
        
        self.emails_list = []
        self.last_results = []
    
    def check_single_email(self):
        email = self.email_var.get().strip()
        if not email:
            messagebox.showwarning("Varning", "Ange en email adress")
            return
        
        self.check_button.config(state='disabled')
        self.status_var.set("Kontrollerar email...")
        self.progress_var.set(0)
        
        # Starta check i background thread
        thread = threading.Thread(target=self._check_single_email_thread, args=(email,))
        thread.daemon = True
        thread.start()
    
    def _check_single_email_thread(self, email):
        self.checker.timeout = self.timeout_var.get()
        result = self.checker.check_email(email)
        self.result_queue.put(('single', result))
    
    def load_email_file(self):
        filename = filedialog.askopenfilename(
            title="Välj email fil",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.emails_list = [line.strip() for line in f if line.strip()]
                
                self.file_label.config(text=f"{len(self.emails_list)} emails laddade")
                self.bulk_check_button.config(state='normal')
                
            except Exception as e:
                messagebox.showerror("Fel", f"Kunde inte läsa fil: {e}")
    
    def check_bulk_emails(self):
        if not self.emails_list:
            messagebox.showwarning("Varning", "Ladda en email fil först")
            return
        
        self.bulk_check_button.config(state='disabled')
        self.load_file_button.config(state='disabled')
        self.status_var.set(f"Kontrollerar {len(self.emails_list)} emails...")
        self.progress_var.set(0)
        self.results_text.delete(1.0, tk.END)
        
        # Starta bulk check i background thread
        thread = threading.Thread(target=self._check_bulk_emails_thread)
        thread.daemon = True
        thread.start()
    
    def _check_bulk_emails_thread(self):
        self.checker.timeout = self.timeout_var.get()
        workers = self.workers_var.get()
        
        total = len(self.emails_list)
        completed = 0
        
        results = []
        
        # Simulera progress genom att köra en åt gången för GUI feedback
        for email in self.emails_list:
            result = self.checker.check_email(email)
            results.append(result)
            completed += 1
            
            progress = (completed / total) * 100
            self.result_queue.put(('progress', progress, result.email))
        
        self.result_queue.put(('bulk_complete', results))
    
    def check_queue(self):
        try:
            while True:
                item = self.result_queue.get_nowait()
                
                if item[0] == 'single':
                    result = item[1]
                    self.display_single_result(result)
                    self.check_button.config(state='normal')
                    self.status_var.set("Klar")
                    self.progress_var.set(100)
                    self.last_results = [result]
                    self.enable_export_buttons()
                
                elif item[0] == 'progress':
                    progress, email = item[1], item[2]
                    self.progress_var.set(progress)
                    self.status_var.set(f"Kontrollerar: {email}")
                
                elif item[0] == 'bulk_complete':
                    results = item[1]
                    self.display_bulk_results(results)
                    self.bulk_check_button.config(state='normal')
                    self.load_file_button.config(state='normal')
                    self.status_var.set("Bulk kontroll klar")
                    self.progress_var.set(100)
                    self.last_results = results
                    self.enable_export_buttons()
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)
    
    def display_single_result(self, result: EmailCheckResult):
        self.results_text.delete(1.0, tk.END)
        
        text = f"Email: {result.email}\n"
        text += "=" * 50 + "\n"
        text += f"✓ Giltig syntax: {result.is_valid_syntax}\n"
        text += f"✓ Domän existerar: {result.domain_exists}\n"
        text += f"✓ SMTP giltig: {result.smtp_valid}\n"
        text += f"✓ Disposable email: {result.is_disposable}\n"
        text += f"✓ Role account: {result.is_role_account}\n"
        text += f"✓ Catch-all: {result.is_catch_all}\n"
        
        if result.mx_records:
            text += f"MX Records: {', '.join(result.mx_records)}\n"
        
        if result.error_message:
            text += f"❌ Fel: {result.error_message}\n"
        
        text += f"Kontroll tid: {result.check_duration:.3f}s\n"
        
        self.results_text.insert(1.0, text)
    
    def display_bulk_results(self, results: List[EmailCheckResult]):
        self.results_text.delete(1.0, tk.END)
        
        # Sammanfattning
        valid_count = sum(1 for r in results if r.smtp_valid)
        invalid_count = sum(1 for r in results if not r.smtp_valid and r.is_valid_syntax)
        syntax_errors = sum(1 for r in results if not r.is_valid_syntax)
        disposable_count = sum(1 for r in results if r.is_disposable)
        role_count = sum(1 for r in results if r.is_role_account)
        
        summary = f"SAMMANFATTNING\n"
        summary += "=" * 50 + "\n"
        summary += f"Totalt kontrollerade: {len(results)}\n"
        summary += f"✓ Giltiga emails: {valid_count}\n"
        summary += f"✗ Ogiltiga emails: {invalid_count}\n"
        summary += f"❌ Syntax fel: {syntax_errors}\n"
        summary += f"📧 Disposable emails: {disposable_count}\n"
        summary += f"🏢 Role accounts: {role_count}\n\n"
        
        # Detaljerade resultat
        summary += "DETALJERADE RESULTAT\n"
        summary += "=" * 50 + "\n"
        
        for result in results:
            status = "✓" if result.smtp_valid else "✗"
            flags = []
            if result.is_disposable:
                flags.append("DISPOSABLE")
            if result.is_role_account:
                flags.append("ROLE")
            if result.is_catch_all:
                flags.append("CATCH-ALL")
            
            flag_text = f" [{', '.join(flags)}]" if flags else ""
            summary += f"{status} {result.email}{flag_text}\n"
            
            if result.error_message:
                summary += f"    Fel: {result.error_message}\n"
        
        self.results_text.insert(1.0, summary)
    
    def enable_export_buttons(self):
        self.export_csv_button.config(state='normal')
        self.export_json_button.config(state='normal')
    
    def export_results(self, format_type):
        if not self.last_results:
            messagebox.showwarning("Varning", "Inga resultat att exportera")
            return
        
        filename = filedialog.asksaveasfilename(
            title=f"Spara {format_type.upper()} fil",
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} files", f"*.{format_type}"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.checker.export_results(self.last_results, format_type, filename)
                messagebox.showinfo("Success", f"Resultat exporterade till {filename}")
            except Exception as e:
                messagebox.showerror("Fel", f"Kunde inte exportera: {e}")

def main():
    root = tk.Tk()
    app = MailCheckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()