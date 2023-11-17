# thermal-printer-fun

CPSC 440 project using a Raspberry Pi + Camera Module V1 + TM-T88V thermal printer to print images

![The project in action](https://github.com/AnOrdinaryUsername/thermal-printer-FUN/assets/57053268/3343bbff-023b-4a95-bfa5-595e228b7895)


## Installation

Clone the repo then go to the repo directory and run the following command.
The `--system-site-packages` flag allows access to packages at the system level, such as `gpiozero`.

```bash
python3 -m venv --system-site-packages .venv
```

Activate the virtual environment
```bash
source .venv/bin/activate
```

Check location of Python interpreter and make sure its in `.venv`
```bash
which python3
```

Install requirements.txt
```bash
python3 -m pip install -r requirements.txt
```

Then create a `.env` file with the following variables

```env
IMAGE_DIR=
VENDOR_ID=
PRODUCT_ID=
IN_EP=
OUT_EP=
```

## Understanding How EPSON Thermal Printers Works

Many thermal printers use the ESC/POS page description language to specify
the appearance of printed pages. The most analogous example would be HTML
for websites; they both describe the content and structure of their targeted
media.

Looking at the [ESC/POS Command Reference](https://download4.epson.biz/sec_pubs/pos/reference_en/escpos/ref_escpos_en/tmt88v.html), one can see the various
commands and their functions laid out. It can be a bit confusing, but for now, pay
attention to the hexadecimal formats.

```
ESC t

[Name] Select character code table
[Format] ASCII   ESC    t  n
         Hex      1B   74  n
         Decimal  27  116  n
```

To get a thermal printer to perform some action, a host computer transfers ESC/POS data via interface (e.g. USB, RS-232, Parallel etc.), and the thermal printer temporarily stores that data in a receive buffer. The printer then sequentially (except for real-time commands) goes through the data inside the buffer, classifying them as a character or a command.

Normal commands perform the function designated to them. In `ESC t`, it uses a specific character code table to determine how
characters should be formatted.

Now that we understand how a thermal printer processes data, the next question is what does that data look like?

Fortunately, the TM-T88V has a hexadecimal dumping mode (see pg. 73 of the [TM-T88V technical reference guide](https://files.support.epson.com/pdf/pos/bulk/tm-t88v_trg_en_revf.pdf))! We can now view all the printed data in hexadecimal format.

After enabling hexadecimal dumping, we can use python-escpos to test out a basic "Hello, World!" and see its
hex output.

**WARNING: Do NOT try to print out an image while hexadecimal dumping is enabled. It will use a MASSIVE amount of thermal paper**

```python
from escpos.printer import Usb

# Make sure your idVendor, idProduct, and endpoints match your own device!
# See https://python-escpos.readthedocs.io/en/latest/user/usage.html#usb-printer
printer = Usb(idVendor=0x04b8, idProduct=0x0202, in_ep=0x82, out_ep=0x01, profile="TM-T88V")
        
printer.text("Hello, World!")
printer.text("\n")
```

Assuming your printer is working properly, it should print out:

```
Hexadecimal Dump
To terminate hexadecimal dump,
press Feed button three times.


1B 74 00 48 65 6C 6C 6F 2C 20    .t.Hello,
57 6F 72 6C 64 21 0A             World!.
```

The right side of the hex numbers lists characters that correspond to the print data.
Dots represent characters that have no corresponding character.

Breaking it down

1B 74 00 --> ESC t (Select character code table 0 which is [PC437](https://download4.epson.biz/sec_pubs/pos/reference_en/charcode/ref_charcode_en/page_00.html))  
48..21 ----> Hello, World!  
0A --------> Line feed (\n)  

For fun, we can create a `.hex` file and send the raw data to the printer to see if it works. Using your hex editor of choice,
copy and paste the hex dump and save it as `hello_world.hex`. We can then run the following command in our Linux terminal to tell the printer
to print our data.

```sh
cat hello_world.hex > /dev/usb/lp0
```

Unsurprisingly, it does indeed work!
