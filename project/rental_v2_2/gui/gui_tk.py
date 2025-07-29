import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, date

def input_date(title="Wybierz datę") -> date | None:
    """Otwiera okno wyboru daty i zwraca ją jako obiekt datetime.date."""

    result = {"date": None}

    class CustomEntry(ttk.Frame):
        def __init__(self, master=None, **kwargs):
            super().__init__(master)
            style = ttk.Style()
            style.configure("Custom.TEntry", fieldbackground='#ffffff', foreground='#333333')
            style.configure("Custom.TButton", fieldbackground='#dddddd', foreground='#333333')

            self.var = tk.StringVar()
            self.var.set(str(date.today()))  # Ustawiamy domyślną datę

            self.entry = ttk.Entry(self, textvariable=self.var,
                                style='Custom.TEntry', width=16)
            self.entry.pack(side="left", fill='x', expand=True)

            self.btn = ttk.Button(self, text="▼", command=self.show_calendar,
                                style="Custom.TButton", width=2)
            self.btn.pack(side="left")

            self.entry.bind('<Button-1>', lambda e: self.show_calendar())
            self.calendar_win = None

        def show_calendar(self):
            if self.calendar_win:
                return

            self.calendar_win = tk.Toplevel(self)
            self.calendar_win.transient(self)
            self.calendar_win.grab_set()

            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height()
            self.calendar_win.geometry(f'250x220+{x}+{y}')

            cal = Calendar(self.calendar_win,
                        date_pattern='yyyy-mm-dd',
                        background='#f8f8f8',
                        foreground='#333333',
                        selectbackground='#1976d2',
                        selectforeground='#ffffff')

            # Ustawiamy kalendarz na dzisiejszą datę
            cal.set_date(self.var.get())

            cal.pack(fill="both", expand=True)

            def select_date():
                selected = cal.get_date()
                self.var.set(selected)
                self.calendar_win.destroy()
                self.calendar_win = None
                update_label()

            cal.bind("<<CalendarSelected>>", lambda e: select_date())
            self.calendar_win.protocol("WM_DELETE_WINDOW",
                                    lambda: self.calendar_win.destroy())
            self.calendar_win.focus_force()

        def get_date(self):
            return self.var.get()

    def update_label():
        result_label.config(text=f"Wybrana data: {date_entry.get_date()}")

    root = tk.Tk()
    root.title(title)
    root.geometry("250x120+200+200")
    root.resizable(False, False)

    date_entry = CustomEntry(root)
    date_entry.pack(padx=10, pady=10)

    result_label = ttk.Label(root, text=f"Wybrana data: {date.today()}")
    result_label.pack(pady=5)

    def confirm():
        date_str = date_entry.get_date()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            result["date"] = dt
        except ValueError:
            result["date"] = None
        root.destroy()

    action_btn = ttk.Button(root, text="Zatwierdź", command=confirm)
    action_btn.pack(pady=5)

    root.mainloop()

    return result["date"]

