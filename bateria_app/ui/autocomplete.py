# ui/autocomplete.py
import tkinter as tk
import ttkbootstrap as ttk

class AutocompleteEntry(ttk.Entry):
    def __init__(self, parent, autocomplete_list=None, placeholder="Digite aqui...", bootstyle=None,
                 on_select_callback=None, max_height=10, *args, **kwargs):
        if bootstyle is None:
            bootstyle = "primary"
        super().__init__(parent, bootstyle=bootstyle, *args, **kwargs)

        self.parent = parent
        self.on_select_callback = on_select_callback
        self.max_height = max_height

        # Lista de sugestões
        if autocomplete_list is None:
            autocomplete_list = []
        self.autocomplete_list = sorted(autocomplete_list, key=str.lower)

        # Variável do Entry
        self.var = tk.StringVar()
        self.config(textvariable=self.var)

        # Placeholder
        self.placeholder = placeholder
        self._has_placeholder = False
        self._set_placeholder()

        # Detecta escrita
        try:
            self.var.trace_add("write", lambda *a: self.changed())
        except Exception:
            self.var.trace("w", self.changed)

        # Eventos
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._set_placeholder)
        self.bind("<Right>", self.selection)
        self.bind("<Down>", self.move_down)
        self.bind("<Up>", self.move_up)
        self.bind("<Button-1>", self.show_all)

        # Listbox e scrollbar
        self.listbox_up = False
        self.listbox_frame = None
        self.listbox = None
        self.scrollbar = None

        # Recupera cores do tema ttkbootstrap
        style = ttk.Style()
        self.bg_color = style.lookup('TEntry', 'fieldbackground') or "#ffffff"
        self.fg_color = style.lookup('TEntry', 'foreground') or "#000000"
        self.sel_bg_color = style.lookup('TEntry', 'selectbackground') or "#0d6efd"
        self.sel_fg_color = style.lookup('TEntry', 'selectforeground') or "#ffffff"

    def _set_placeholder(self, *args):
        if not self.var.get():
            self._has_placeholder = True
            self.var.set(self.placeholder)
            self.config(foreground="grey")

    def _clear_placeholder(self, *args):
        if self._has_placeholder:
            self.var.set("")
            self.config(foreground=self.fg_color)
            self._has_placeholder = False

    def show_all(self, event=None):
        self._clear_placeholder()
        self.changed()

    def update_list(self, new_list):
        self.autocomplete_list = sorted(new_list, key=str.lower)
        if self.listbox_up:
            self.changed()

    def changed(self, *args):
        if self._has_placeholder:
            return
        txt = self.var.get()
        words = self.autocomplete_list if txt == "" else self.matches(txt)

        if words:
            if not self.listbox_up:
                self.open_listbox()
            self.listbox.delete(0, "end")
            for w in words:
                self.listbox.insert("end", w)
            # Ajusta a altura da listbox
            altura = min(len(words), self.max_height)
            self.listbox.config(height=altura)
        else:
            self.close_listbox()

    def matches(self, text):
        text_l = text.lower()
        return [w for w in self.autocomplete_list if text_l in w.lower()]

    def selection(self, event):
        if self.listbox_up and self.listbox.curselection():
            self._select_current()
        return "break"

    def move_up(self, event):
        if not self.listbox_up:
            return "break"
        cur = self.listbox.curselection()
        idx = cur[0] if cur else 0
        if idx > 0:
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(idx - 1)
            self.listbox.activate(idx - 1)
        return "break"

    def move_down(self, event):
        if not self.listbox_up:
            return "break"
        cur = self.listbox.curselection()
        idx = cur[0] if cur else -1
        if idx < self.listbox.size() - 1:
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(idx + 1)
            self.listbox.activate(idx + 1)
        return "break"

    def open_listbox(self):
        if self.listbox_up:
            return

        # Toplevel flutuante
        self.listbox_frame = tk.Toplevel(self)
        self.listbox_frame.wm_overrideredirect(True)  # sem bordas
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.listbox_frame.wm_geometry(f"{self.winfo_width()}x100+{x}+{y}")  # altura inicial, ajustável

        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical")
        self.listbox = tk.Listbox(
            self.listbox_frame,
            yscrollcommand=self.scrollbar.set,
            background=self.bg_color,
            foreground=self.fg_color,
            selectbackground=self.sel_bg_color,
            selectforeground=self.sel_fg_color
        )
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)

        self.listbox.bind("<<ListboxSelect>>", lambda e: self._select_current())
        self.listbox.bind("<Right>", self.selection)

        self.listbox_up = True


    def _select_current(self):
        sel = self.listbox.curselection()
        if sel:
            self.var.set(self.listbox.get(sel[0]))
            self.close_listbox()
            self.icursor("end")
            if self.on_select_callback:
                self.on_select_callback(self.var.get())

    def close_listbox(self):
        if self.listbox_up:
            try:
                self.listbox_frame.destroy()
            except Exception:
                pass
        self.listbox_up = False
        self.listbox_frame = None
        self.listbox = None
        self.scrollbar = None