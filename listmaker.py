import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.style import Style


class MainApplication(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Settings for customizing list
        self.title = ttk.StringVar(value="")
        self.list_type = ttk.StringVar(value="checkbox")
        self.notes = ttk.StringVar(value="")
        self.has_notes = ttk.BooleanVar(value=True)
        self.notes_frame = ttk.Labelframe(
            self.master, text="Add Extra Notes", padding=(20, 10)
        )
        self.has_separators = ttk.BooleanVar(value=False)
        # End settings

        # Keeps track of all entries
        self.entries = []

        self.list_customization = ListCustomization(
            self.master,
            self.title,
            self.list_type,
            self.notes,
            self.has_notes,
            self.has_separators,
            self.show_notes,
        )
        self.list_entries = ListEntries(self.master, self.entries)

        self.list_customization.grid(row=0, column=0, padx=15, pady=15)
        self.list_entries.grid(row=1, column=0, padx=15, pady=15)
        self.show_notes()
        self.create_buttonbox()

        # print(self.winfo_screenheight())
        
    def show_notes(self):
        if not self.has_notes.get():
            self.notes_frame.destroy()
            self.notes = ttk.StringVar(value="")
            return

        self.notes_frame = ttk.Labelframe(
            self.master, text="Add Extra Notes", padding=(20, 10)
        )
        self.notes_frame.grid(
            row=0, rowspan=2, column=1, sticky="nsew", padx=15, pady=15
        )

        label = ttk.Label(master=self.notes_frame, text="Notes", width=10)
        label.pack(side=TOP, fill=X, padx=5)

        ent = ttk.Text(master=self.notes_frame, wrap="word", height=1, width=75)
        self.notes = ent.get("1.0", "end-1c")
        ent.pack(side=BOTTOM, padx=5, pady=10, fill=BOTH, expand=YES)

    def create_buttonbox(self):
        container = ttk.Frame(self.master, bootstyle=DARK)
        container.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # White text on light green makes it hard to read the button text.
        # This changes the foreground to black
        style = Style()
        style.configure(
            "success.Outline.TButton", foreground="#000000", background="#14a98b"
        )

        sub_btn = ttk.Button(
            master=container,
            text="Submit",
            command=self.on_submit,
            bootstyle=(OUTLINE, SUCCESS),
            width=6,
            style="success.Outline.TButton",
        )
        sub_btn.pack(side=RIGHT, padx=15, pady=10)

    def on_submit(self):
        print("pog")


class ListCustomization(ttk.Labelframe):
    def __init__(
        self, master, title, list_type, notes, has_notes, has_separators, show_notes
    ):
        super().__init__(master=master, text="Customize Your List", padding=(20, 10))

        self.title = title
        self.list_type = list_type
        self.notes = notes
        self.has_notes = has_notes
        self.has_separators = has_separators

        self.create_radio_row("List Type")
        self.create_form_entry("Title", self.title)
        self.create_checkbutton(
            text="Include notes section",
            variable=self.has_notes,
            command=show_notes,
        )
        self.create_checkbutton(
            text="Show separators",
            variable=self.has_separators,
            command=(lambda x=self.has_separators: not x),
        )

    def create_form_entry(self, label, variable):
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES, pady=5)

        label = ttk.Label(master=container, text=label.title(), width=10)
        label.pack(side=LEFT, padx=5)

        ent = ttk.Entry(master=container, textvariable=variable)
        ent.pack(side=LEFT, padx=5, fill=X, expand=YES)

    def create_radio_row(self, label):
        type_row = ttk.Frame(self)
        type_row.pack(fill=X, expand=YES)
        type_label = ttk.Label(type_row, text=label.title(), width=10)
        type_label.pack(side=LEFT, padx=5, pady=10)

        checkbox_opt = ttk.Radiobutton(
            master=type_row, text="Checkbox", variable=self.list_type, value="checkbox"
        )
        checkbox_opt.pack(side=LEFT)

        bullet_opt = ttk.Radiobutton(
            master=type_row,
            text="Bullet Points",
            variable=self.list_type,
            value="bullet",
        )
        bullet_opt.pack(side=LEFT, padx=15)

        number_opt = ttk.Radiobutton(
            master=type_row, text="Numbered", variable=self.list_type, value="number"
        )
        number_opt.pack(side=LEFT)
        number_opt.invoke()

    def create_checkbutton(self, text, variable, command):
        check_row = ttk.Frame(self)
        check_row.pack(fill=X, expand=YES)
        label = ttk.Frame(master=check_row, width=10)
        label.pack(side=LEFT, padx=5, pady=10)

        ttk.Checkbutton(
            label,
            text=text,
            variable=variable,
            command=command,
            bootstyle="round-toggle",
        ).pack(side=RIGHT)


class ListEntries(ttk.Labelframe):
    def __init__(self, master, entries):
        super().__init__(master=master, text="Enter Entries", padding=(20, 10))

        self.entries = entries

        header_txt = "Entry Data"
        header = ttk.Label(master=self, text=header_txt, width=50)
        header.pack(fill=X, padx=5, pady=10)

        # Changes foreground color to black since white on yellow is too light
        style = Style()
        style.configure("primary.TButton", foreground="#000000")
        sub_btn = ttk.Button(
            master=self,
            text="Add Entry",
            command=self.on_add_entry,
            bootstyle=PRIMARY,
            style="primary.TButton",
        )
        sub_btn.pack(side=BOTTOM, padx=5, pady=10)

        for i in range(5):
            self.create_form_entry(i)

    def create_form_entry(self, index, entry_text=""):
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES, pady=5)

        text = ttk.StringVar(value=entry_text)
        self.entries.append(text)

        label = ttk.Label(master=container, text=f"Entry {index + 1}", width=10)
        label.pack(side=LEFT, padx=5)

        ent = ttk.Entry(master=container, textvariable=text)
        ent.pack(side=LEFT, padx=5, fill=X, expand=YES)

        sub_btn = ttk.Button(
            master=container,
            text="Delete",
            command=self.on_delete,
            bootstyle=(OUTLINE, DANGER),
            width=6,
        )
        sub_btn.pack(side=RIGHT, padx=5)

    def on_add_entry(self):
        self.create_form_entry(len(self.entries))

    def on_delete(self):
        print("Pog")


if __name__ == "__main__":
    app = ttk.Window(title="List Maker", themename="solar", resizable=(False, True))
    MainApplication(app)
    app.place_window_center()

    app.mainloop()
