"""Hospital Management System (short version) - Tkinter + SQLite
Run: python hospital_short.py     Login: admin / admin123"""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

TABS = {"patients": ["name", "age", "phone", "disease"],
        "doctors": ["name", "specialization", "phone"],
        "appointments": ["patient_id", "doctor_id", "date"],
        "billing": ["patient_id", "amount"]}
NUMERIC = ("age", "patient_id", "doctor_id", "amount")


def q(sql, p=(), get=False):
    with sqlite3.connect("hospital.db") as c:
        r = c.execute(sql, p)
        return r.fetchall() if get else None


def init_db():
    for t, f in TABS.items():
        q(f"CREATE TABLE IF NOT EXISTS {t}(id INTEGER PRIMARY KEY AUTOINCREMENT,"
          f"{','.join(x + ' TEXT' for x in f)})")


class Crud(ttk.Frame):
    def __init__(self, parent, table, fields):
        super().__init__(parent, padding=10)
        self.table, self.fields, self.sel = table, fields, None
        self.vars = {f: tk.StringVar() for f in fields}
        form = ttk.Frame(self); form.pack(fill="x")
        for i, f in enumerate(fields):
            ttk.Label(form, text=f.replace("_", " ").title()).grid(row=0, column=i, padx=4)
            ttk.Entry(form, textvariable=self.vars[f], width=16).grid(row=1, column=i, padx=4)
        bar = ttk.Frame(self); bar.pack(pady=8)
        for t, c in [("Add", self.add), ("Update", self.update),
                     ("Delete", self.delete), ("Clear", self.clear)]:
            ttk.Button(bar, text=t, command=c).pack(side="left", padx=4)
        cols = ["id"] + fields
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c.title()); self.tree.column(c, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.pick)
        self.refresh()

    def values(self):
        v = [self.vars[f].get().strip() for f in self.fields]
        if not all(v):
            return messagebox.showerror("Error", "Fill all fields")
        for f, x in zip(self.fields, v):
            if f in NUMERIC and not x.replace(".", "", 1).isdigit():
                return messagebox.showerror("Error", f"{f} must be a number")
        return v

    def add(self):
        v = self.values()
        if v:
            q(f"INSERT INTO {self.table}({','.join(self.fields)}) VALUES({','.join('?' * len(v))})", v)
            self.clear()

    def update(self):
        v = self.values()
        if v and self.sel:
            q(f"UPDATE {self.table} SET {','.join(f + '=?' for f in self.fields)} WHERE id=?",
              v + [self.sel])
            self.clear()

    def delete(self):
        if self.sel and messagebox.askyesno("Confirm", "Delete this record?"):
            q(f"DELETE FROM {self.table} WHERE id=?", (self.sel,))
            self.clear()

    def clear(self):
        self.sel = None
        for v in self.vars.values():
            v.set("")
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for r in q(f"SELECT id,{','.join(self.fields)} FROM {self.table}", get=True):
            self.tree.insert("", "end", values=r)

    def pick(self, _):
        s = self.tree.selection()
        if s:
            self.sel = self.tree.item(s[0])["values"][0]
            row = q(f"SELECT {','.join(self.fields)} FROM {self.table} WHERE id=?", (self.sel,), True)[0]
            for f, x in zip(self.fields, row):
                self.vars[f].set(x)


def main_window(root):
    for w in root.winfo_children():
        w.destroy()
    nb = ttk.Notebook(root); nb.pack(fill="both", expand=True)
    for t, f in TABS.items():
        nb.add(Crud(nb, t, f), text=t.title())


def login_window(root):
    u, p = tk.StringVar(), tk.StringVar()
    box = ttk.LabelFrame(root, text="Login", padding=20); box.place(relx=.5, rely=.4, anchor="center")
    ttk.Label(box, text="Username").grid(row=0, column=0, pady=4)
    ttk.Entry(box, textvariable=u).grid(row=0, column=1)
    ttk.Label(box, text="Password").grid(row=1, column=0, pady=4)
    ttk.Entry(box, textvariable=p, show="*").grid(row=1, column=1)
    ttk.Button(box, text="Login", command=lambda: main_window(root)
               if (u.get(), p.get()) == ("admin", "admin123")
               else messagebox.showerror("Error", "Wrong username or password")).grid(columnspan=2, pady=10)


if __name__ == "__main__":
    init_db()
    root = tk.Tk(); root.title("Hospital Management System"); root.geometry("750x420")
    login_window(root)
    root.mainloop()