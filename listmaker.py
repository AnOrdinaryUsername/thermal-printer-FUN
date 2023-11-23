import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.style import Style
from functools import partial

# For Image Creation
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap


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

        self.list_customization = ListCustomization(
            self.master,
            self.title,
            self.list_type,
            self.has_notes,
            self.has_separators,
            self.show_notes,
        )
        self.list_entries = ListEntries(self.master, self.entries)

        self.list_customization.grid(row=0, column=0, padx=15, pady=15, sticky=NSEW)
        self.list_entries.grid(row=1, column=0, padx=15, pady=15)
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

        self.notes_box = ttk.Text(
            master=self.notes_frame, wrap="word", height=1, width=75
        )
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
            command=self.on_submit,
            bootstyle=(OUTLINE, SUCCESS),
            width=6,
            style="success.Outline.TButton",
        )
        submit_btn.pack(side=RIGHT, padx=15)

        preview_btn = ttk.Button(
            master=container,
            text="Preview",
            command=self.on_submit,
            bootstyle=LIGHT,
            width=7,
        )
        preview_btn.pack(side=RIGHT, pady=10)

    def on_submit(self):
        # "1.0" ----> Input should be read from line one, character zero
        # "end-1c" -> Read until the end of the text box is reached and delete newline char
        # https://stackoverflow.com/a/14824164
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

        self.preview_list(options)

    def preview_list(self, options):
        """
        512 is the max-width of the TM-T88V
        1200 is just a large number due to the fact
        we can't dynamically resize the image
        """
        width, height = 512, 1200
        background_color = "white"
        text_color = "black"
        line_spacing = 30
        margin = 20

        # List types
        black_square = "\u25AA"
        bullet_point = "\u2022"
        checkbox = "\u25A2"

        # Load a font
        font = ImageFont.truetype(
            os.path.join(os.getcwd(), "assets", "Iosevka-Extended.ttf"),
            24,
            encoding="utf-16",
        )
        bold_font = ImageFont.truetype(
            os.path.join(os.getcwd(), "assets", "Iosevka-ExtendedBold.ttf"),
            32,
            encoding="utf-16",
        )

        # For now, create a transparent image so that we can crop it later
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        y = margin
        # Title text
        draw.multiline_text(
            (margin, y),
            f'{options["title"]}',
            fill=text_color,
            font=bold_font,
            align="center",
        )
        y += line_spacing

        # Empty line space
        draw.text((margin, y), "\n")
        y += line_spacing

        # Add tasks to the image
        if options["list_type"] == "number":
            entries = options["entries"]
            entries_count = len(entries)
            last = entries_count - 1

            for number in range(entries_count):
                draw.text(
                    (margin, y),
                    f"{number + 1}) {entries[number]}",
                    fill=text_color,
                    font=font,
                )
                y += line_spacing

                if options["has_separators"]:
                    if number != last:
                        draw.line((0, 0, margin, y), "black")

        else:
            for task in options["entries"]:
                draw.text(
                    (margin, y), checkbox + f" {task}", fill=text_color, font=font
                )
                y += line_spacing

        # Empty line space
        draw.text((margin, y), "\n")
        y += line_spacing * 2

        if options["has_notes"]:
            draw.text((margin, y), "Notes:", fill=text_color, font=font)
            y += line_spacing
            draw.multiline_text(
                (margin, y), options["notes"], fill=text_color, font=font
            )

        print(image.width)

        # See image in this for help: https://stackoverflow.com/a/71532590
        bounding_box = image.getbbox()
        cropped_image = image.crop([0, 0, width, bounding_box[3] + margin])

        list_image = Image.new("RGBA", cropped_image.size, background_color)
        list_image.paste(cropped_image, (0, 0), cropped_image)

        print(list_image.width)

        list_image.show()


class ListCustomization(ttk.Labelframe):
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
        super().__init__(master=master, text="Enter Entries", padding=(20, 0, 0))

        self.entries = entries

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
            text="Delete",
            command=partial(self.on_delete, index),
            bootstyle=(OUTLINE, DANGER),
            width=6,
        )
        sub_btn.pack(side=RIGHT, padx=5)

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
