import os
from PIL import Image, UnidentifiedImageError

from image import ListImage

# For making the GUI
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.style import Style
from ttkbootstrap.dialogs.dialogs import Messagebox
from functools import partial

# For Printing
from escpos.printer import Usb
from escpos.exceptions import Error
import traceback


class MainApplication(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Settings for customizing list
        self.title = ttk.StringVar(value="")
        self.list_type = ttk.StringVar(value="checkbox")
        self.has_notes = ttk.BooleanVar(value=True)
        self.has_separators = ttk.BooleanVar(value=False)
        # End settings

        # Keeps track of all entries
        self.entries = []

        # Keeps track of notes section
        self.notes_frame = None
        self.notes_box = None
        self.notes = ""

        # The image with the list for printing
        self.list_image = ListImage()

        # Add trash icon to delete button in entries
        trash_png_path = os.path.join(os.getcwd(), "assets", "trash.png")
        trash_hover_png_path = os.path.join(os.getcwd(), "assets", "trash-solid.png")
        self.trash_icon = ttk.PhotoImage(file=trash_png_path)
        self.trash_hover_icon = ttk.PhotoImage(file=trash_hover_png_path)


        self.list_customization = Customization(
            self.master,
            self.title,
            self.list_type,
            self.has_notes,
            self.has_separators,
            self.show_notes,
        )
        self.list_entries = ListItems(
            self.master, self.entries, self.trash_icon, self.trash_hover_icon
        )

        self.list_customization.grid(row=0, column=0, padx=15, pady=15, sticky=NSEW)
        self.list_entries.grid(row=1, column=0, padx=15, pady=15, sticky=NSEW)
        self.show_notes()
        self.create_buttonbox()

    def show_notes(self):
        if not self.has_notes.get():
            self.notes_frame.destroy()
            self.notes = ""
            return

        self.notes_frame = ttk.Labelframe(
            self.master, text="Add Extra Notes", padding=(20, 10)
        )
        self.notes_frame.grid(
            row=0, rowspan=2, column=1, sticky="nsew", padx=15, pady=15
        )

        label = ttk.Label(master=self.notes_frame, text="Notes", width=10)
        label.pack(side=TOP, fill=X, padx=5)

        self.notes_box = ttk.Text(master=self.notes_frame, wrap="word", height=1)
        self.notes_box.pack(side=BOTTOM, padx=5, pady=10, fill=BOTH, expand=YES)

    def create_buttonbox(self):
        container = ttk.Frame(self.master, bootstyle=DARK)
        container.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # White text on light green makes it hard to read the button text.
        # This changes the foreground to black
        style = Style()
        style.configure(
            "success.Outline.TButton", foreground="#000000", background="#14a98b"
        )

        submit_btn = ttk.Button(
            master=container,
            text="Submit",
            command=self.print_image_list,
            bootstyle=(OUTLINE, SUCCESS),
            width=6,
            style="success.Outline.TButton",
        )
        submit_btn.pack(side=RIGHT, padx=15)

        preview_btn = ttk.Button(
            master=container,
            text="Preview",
            command=self.preview_list,
            bootstyle=LIGHT,
            width=7,
        )
        preview_btn.pack(side=RIGHT, pady=10)

        save_btn = ttk.Button(
            master=container,
            text="Save Image",
            command=self.save_image,
            bootstyle=(OUTLINE, INFO),
            width=10,
        )
        save_btn.pack(side=LEFT, padx=15)

    def get_settings(self):
        if self.has_notes.get():
            self.notes = self.notes_box.get("1.0", "end-1c")

        options = {
            "list_type": self.list_type.get(),
            "title": self.title.get(),
            "has_notes": self.has_notes.get(),
            "has_separators": self.has_separators.get(),
        }

        all_entries = [entry.get() for entry in self.entries]
        # Removes all entries that are only whitespace
        text_entries = list(filter(lambda entry: entry.strip(), all_entries))
        options["entries"] = text_entries

        if self.has_notes.get():
            options["notes"] = self.notes

        print(options)

        return options

    def print_image_list(self):
        options = self.get_settings()
        list_image = self.construct_image(options)

        if not list_image:
            return

        """
        Tells the printer to print the image
        """
        try:
            printer = Usb(
                idVendor=int(os.environ["VENDOR_ID"], 16),
                idProduct=int(os.environ["PRODUCT_ID"], 16),
                in_ep=int(os.environ["IN_EP"], 16),
                out_ep=int(os.environ["OUT_EP"], 16),
                profile="TM-T88V",
            )

            printer.image(list_image)
            printer.cut()

        except Error as err:
            traceback.print_exc()
            print(f"ERROR {err.resultcode}: {err.msg}")

    def preview_list(self):
        options = self.get_settings()
        title = options["title"] or "Image"
        
        image = self.construct_image(options)
        
        if image:
            image.show(title)

    def construct_image(self, options):
        image = None

        try:
            self.list_image.generate(options)
            
            image = Image.open(self.list_image.bytes)
        except TypeError:
            Messagebox.show_error(message="The image is empty. Did you enter any data?", title="Empty Image")
        except UnidentifiedImageError:
            Messagebox.show_error(message="There is an issue with the image bytes.", title="UnidentifiedImageError")

        return image


    def save_image(self):
        options = self.get_settings()
        title = options["title"] or "image"
        
        image = self.construct_image(options)

        if image:
            image.save(f"{title}.png")


class Customization(ttk.Labelframe):
    def __init__(self, master, title, list_type, has_notes, has_separators, show_notes):
        super().__init__(master=master, text="Customize Your List", padding=(20, 10))

        self.title = title
        self.list_type = list_type
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
        container.pack(fill=X, expand=YES, pady=15)

        label = ttk.Label(master=container, text=label.title(), width=10)
        label.pack(side=LEFT, padx=5)

        ent = ttk.Entry(master=container, textvariable=variable)
        ent.pack(side=LEFT, fill=X, expand=YES)

    def create_radio_row(self, label):
        type_row = ttk.Frame(self)
        type_row.pack(fill=X, expand=YES)
        type_label = ttk.Label(type_row, text=label.title(), width=10)
        type_label.grid(row=0, column=0, padx=5, pady=10)

        checkbox_opt = ttk.Radiobutton(
            master=type_row, text="Checkbox", variable=self.list_type, value="checkbox"
        )
        checkbox_opt.grid(row=0, column=1, sticky=W)

        bullet_opt = ttk.Radiobutton(
            master=type_row,
            text="Bullet Points",
            variable=self.list_type,
            value="bullet",
        )
        bullet_opt.grid(row=0, column=2, sticky=W, padx=15)

        number_opt = ttk.Radiobutton(
            master=type_row, text="Numbered", variable=self.list_type, value="number"
        )
        number_opt.grid(row=0, column=3, sticky=W)
        number_opt.invoke()

        arrow_opt = ttk.Radiobutton(
            master=type_row, text="Arrow", variable=self.list_type, value="arrow"
        )
        arrow_opt.grid(row=1, column=1, sticky=W)

        arrowhead_opt = ttk.Radiobutton(
            master=type_row, text="Arrowhead", variable=self.list_type, value="arrowhead"
        )
        arrowhead_opt.grid(row=1, column=2, sticky=W, padx=15)

        triangle_opt = ttk.Radiobutton(
            master=type_row, text="Triangle", variable=self.list_type, value="triangle"
        )
        triangle_opt.grid(row=1, column=3, sticky=W)

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


class ListItems(ttk.Labelframe):
    def __init__(self, master, entries, trash, trash_hover):
        super().__init__(master=master, text="Enter Entries", padding=(20, 0, 0))

        self.entries = entries
        self.trash_icon = trash
        self.trash_hover_icon = trash_hover

        # The following creates the scrollbar inside the Labelframe
        self.canvas = ttk.Canvas(self)
        self.canvas.pack(side=LEFT, fill=Y, expand=YES)

        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=RIGHT, fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.frame_inside_canvas = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_inside_canvas, anchor="nw")
        self.frame_inside_canvas.bind(
            "<Configure>",
            lambda event, canvas=self.canvas: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )
        self.master.bind_all("<MouseWheel>", self.on_mousewheel)
        # End scrollbar creation

        header_txt = "Entry Data"
        header = ttk.Label(master=self.frame_inside_canvas, text=header_txt, width=50)
        header.pack(fill=X, padx=5, pady=10)

        # Changes foreground color to black since white on yellow is too light
        style = Style()
        style.configure("primary.TButton", foreground="#000000")
        sub_btn = ttk.Button(
            master=self.frame_inside_canvas,
            text="Add Entry",
            command=self.on_add_entry,
            bootstyle=PRIMARY,
            style="primary.TButton",
        )
        sub_btn.pack(side=BOTTOM, padx=5, pady=10)

        # Create 5 form entries at the start
        for i in range(5):
            self.create_form_entry(i)

    def create_form_entry(self, index, new_frame=True):
        container = ttk.Frame(self.frame_inside_canvas)
        container.pack(fill=X, expand=YES, pady=5)

        try:
            text = self.entries[index]
        except IndexError:
            text = ttk.StringVar(value="")

        if new_frame:
            self.entries.append(text)

        label = ttk.Label(master=container, text=f"Entry {index + 1}", width=10)
        label.pack(side=LEFT, padx=5)

        ent = ttk.Entry(master=container, textvariable=text)
        ent.pack(side=LEFT, padx=5, fill=X, expand=YES)

        sub_btn = ttk.Button(
            master=container,
            image=self.trash_icon,
            compound=LEFT,
            command=partial(self.on_delete, index),
            bootstyle=(OUTLINE, DANGER),
        )
        sub_btn.pack(side=RIGHT, padx=5)

        # Changes button image to white on hover and pink on leave
        sub_btn.bind(
            "<Enter>", lambda event: sub_btn.config(image=self.trash_hover_icon)
        )
        sub_btn.bind("<Leave>", lambda event: sub_btn.config(image=self.trash_icon))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_add_entry(self):
        self.create_form_entry(len(self.entries))

    def on_delete(self, index):
        self.entries.pop(index)

        # Destroy all form entry frames to update UI
        for child in self.frame_inside_canvas.winfo_children():
            if isinstance(child, ttk.Frame):
                child.destroy()

        # Rerender forms with updated index
        for i in range(len(self.entries)):
            self.create_form_entry(i, new_frame=False)


if __name__ == "__main__":
    app = ttk.Window(title="List Maker", themename="solar", resizable=(False, False))
    MainApplication(app)
    app.place_window_center()

    app.mainloop()
