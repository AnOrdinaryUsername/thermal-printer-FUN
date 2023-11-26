# For Image Creation
from PIL import Image, ImageDraw, ImageFont
import os
import io
import textwrap
import traceback
from dataclasses import astuple, dataclass

# Unicode characters for list symbols
BULLET_POINT = "\u2022"
CHECKBOX = "\u25A2"
ARROW = "\u2b62"
ARROWHEAD = "\u27a4"
TRIANGULAR_BULLET = "\u2023"


@dataclass
class ImageSettings:
    width: int
    height: int
    bg_color: str
    text_color: str
    line_spacing: int
    margin: int

    def __iter__(self):
        return iter(astuple(self))
    
    def __getitem__(self, keys):
        return iter(getattr(self, k) for k in keys)


class ListImage:
    def __init__(self):
        """
        512 is the max-width of the TM-T88V
        6000 is just a large number due to the fact
        we can't dynamically resize the image
        """
        self.settings = ImageSettings(
            width=512,
            height=6000,
            bg_color="white",
            text_color="black",
            line_spacing=30,
            margin=20,
        )

        # Load a font
        self.font = ImageFont.truetype(
            os.path.join(os.getcwd(), "assets", "Iosevka-Extended.ttf"),
            24,
            encoding="utf-16",
        )
        self.bold_font = ImageFont.truetype(
            os.path.join(os.getcwd(), "assets", "Iosevka-ExtendedBold.ttf"),
            32,
            encoding="utf-16",
        )

        self.bytes = None
        self._y_position = self.settings.margin
        print("CHECKBOX px", self.font.getlength(CHECKBOX))
        print("BULLET px", self.font.getlength(BULLET_POINT))
        print("ARROW px", self.font.getlength(ARROW))
        print("TRIANGULAR_BULLET px", self.font.getlength(TRIANGULAR_BULLET))
        print("ARROWHEAD px", self.font.getlength(ARROWHEAD))



    def draw_text(self, draw: ImageDraw, text: str, max_width: int, font: ImageFont, indent_offset=" ", x_offset=0) -> None:
        """
        Iosevka is a monospaced font which means that each font character
        has a fixed-width (except for CHECKBOX and some other unicode characters)

        textwrap.wrap() automatically handles the hard work of wrapping text
        """
        text_color = self.settings.text_color 
        line_spacing= self.settings.line_spacing

        txt_width = font.getlength(text)

        if txt_width < max_width:
            draw.text(
                    (self.settings.margin, self._y_position),
                    text,
                    fill=text_color,
                    font=font,
                )
            self.adjust_y_position(line_spacing)
        else:
            indent = font.getlength(indent_offset)
            char_count = len(indent_offset)
            avg_char_width = indent / char_count
            print("CHAR WIDTH", avg_char_width)

            """
            Bold Title Font = 19
            Regular Font = 14

            Checkbox + space = (29px + 14px) / 2 = 21.5
            Bullet + space = (14px*2) / 2 = 14
            Number + ) + space = (14px*3) / 3 = 14

            We set char_width to 14 for Checkbox since
            margin = 20
            max_width = 512 - (margin * 2) = 472
            472 // 14 = 33 characters (the max we can go before the text goes off image 
                                        since wrap only accepts int)
            """
            char_width = avg_char_width if avg_char_width < 20 else 14
            print(char_width)
           
            # Floor division so we don't accidentally go over the margin
            lines = textwrap.wrap(text, width=int(max_width // char_width))
            symbol_line = lines[0]
            indent_lines = lines[1:]

            if indent_offset != " ":
                indent_str = " ".join(indent_lines)
                indent_lines = textwrap.wrap(indent_str, width=((max_width - indent) // char_width))

            draw.text((x_offset, self._y_position), symbol_line, fill=text_color, font=font)
            self.adjust_y_position(line_spacing)
            
            for line in indent_lines:
                x = x_offset
                
                if indent_offset != " ":
                    x += indent
                
                draw.text((x, self._y_position), line, fill=text_color, font=font)
                self.adjust_y_position(line_spacing)
    
    def adjust_y_position(self, y_offset):
        self._y_position += y_offset

    def generate(self, options):
        """
        To create the image with our list, we use the ImageDraw module from Pillow.
        See: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html

        It uses a coordinate (x, y) based system as seen below:

            (0, 0)  +-----------------------+
                    |  +-----------------+  |
                    |  |                 |  |
                    |  |                 |  |
                    |  |                 |  |
                    |  |                 |  |
                    |  |                 |  |
                    |  |                 |  |
                    |  |     Image       |  |
                    |  |               --+--+----------- Content
                    |  |                 |  |
                    |  |                 |  |
                    |  |                 |  |
                    |  |                 | -+---------- Margin
                    |  |                 |  |
                    |  |                 |  |
                    |  +-----------------+  |
                    +-----------------------+ (512, 1200)
        
        Margin is the blank gap between the content (20 pixels on 4 sides).
        Line spacing adjusts the y-coordinates (vertical position).
        """

        width, height, bg_color, text_color, line_spacing, margin = self.settings

        """
        For now, create a transparent image so that we can crop it later
        using Image.getbbox() and Image.crop()
        """
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        max_width = width - (margin * 2)

        # Title text
        self.draw_text(
            draw,
            text=f'{options["title"]}',
            max_width=max_width,
            font=self.bold_font,
            x_offset=margin
        )
      
        self.adjust_y_position(line_spacing)

        entries = options["entries"]
        entries_count = len(entries)
        last = entries_count - 1
        
        # Add entries to the image
        if options["list_type"] == "number":
            for number in range(entries_count):
                symbol = f"{number + 1})"
                symbol_offset = f"{symbol} "
                entry = f"{symbol} {entries[number]}"
                
                self.draw_text(draw, text=entry, font=self.font, x_offset=margin, max_width=max_width, indent_offset=symbol_offset)

                if options["has_separators"]:
                    if number != last:
                        # Half of an empty line space
                        self.adjust_y_position(line_spacing / 2)

                        draw.line(
                            (0 + margin, self._y_position, width - margin, self._y_position), width=2, fill="black"
                        )

                        # Half of an empty line space
                        self.adjust_y_position(line_spacing / 2)
        else:
            list_type = None

            match options["list_type"]:
                case "bullet":
                    list_type = BULLET_POINT
                case "checkbox":
                    list_type = CHECKBOX
                case "arrow":
                    list_type = ARROW
                case "arrowhead":
                    list_type = ARROWHEAD
                case "triangle":
                    list_type = TRIANGULAR_BULLET
                

            for number in range(entries_count):
                entry = f"{list_type} {entries[number]}"
                symbol_offset = f"{list_type} "
                self.draw_text(draw, text=entry, font=self.font, x_offset=margin, max_width=max_width, indent_offset=symbol_offset)

                if options["has_separators"]:
                    if number != last:
                        # Half of an empty line space
                        self.adjust_y_position(line_spacing / 2)

                        draw.line(
                            (0 + margin, self._y_position, width - margin, self._y_position), width=2, fill="black"
                        )

                        # Half of an empty line space
                        self.adjust_y_position(line_spacing / 2)

        # Two empty lines
        self.adjust_y_position(line_spacing * 2)

        if options["has_notes"]:
            draw.text((margin, self._y_position), "Notes:", fill=text_color, font=self.font)
            self.adjust_y_position(line_spacing)
            self.adjust_y_position(line_spacing / 2)
            self.draw_text(draw, text=options["notes"], font=self.font, x_offset=margin, max_width=max_width)


        print(image.width)

        # See image in this for help: https://stackoverflow.com/a/71532590
        bounding_box = image.getbbox()
        cropped_image = None

        try:
            cropped_image = image.crop([0, 0, width, bounding_box[3] + margin])
        except TypeError as err:
            # Reset y coords
            self._y_position = margin

            traceback.print_exc()
            print("ERROR: Image is empty")
            
            raise TypeError

        list_image = Image.new("RGBA", cropped_image.size, bg_color)
        list_image.paste(cropped_image, (0, 0), cropped_image)

        print(list_image.width)

        image_bytes = io.BytesIO()
        list_image.save(image_bytes, format="PNG")
        self.bytes = image_bytes

        # Reset y coords
        self._y_position = margin
