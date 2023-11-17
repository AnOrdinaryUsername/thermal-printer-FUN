from gpiozero import Button, DigitalOutputDevice, RGBLED
from signal import pause
from picamera2 import Picamera2, Preview
from escpos.printer import Usb
from escpos.exceptions import Error
import time
import os
import traceback
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# RGB LED colors
YELLOW = (0.5, 0.5, 0)
BLUE   = (0, 0, 0.5)
GREEN  = (0, 0.5, 0)
RED    = (0.5, 0, 0)

picam2 = Picamera2()
led = RGBLED(red=14, green=15, blue=18)

def play_tone(frequency, duration):
    """
    Note: I'm using a passive buzzer (piezo transducer) 
    that needs an external oscillating signal. This is 
    different from a self-oscillating active buzzer.
    
    Passive buzzers can play a variety of tones with pitch control
    just by changing the frequency and duration of the signal.
    
    Differences explained here:
    https://arduinogetstarted.com/tutorials/arduino-piezo-buzzer
    
    :param frequency: Frequency of tone in hertz (hz)
    :param duration: Time in seconds
    """
    pin_1 = DigitalOutputDevice(16)
    pin_2 = DigitalOutputDevice(21)
    
    # T = 1 / f
    # where T is the time to complete one cycle
    # and f is frequency in hertz
    period = 1.0 / frequency
    # For a 50% duty cycle
    pulse_width = period / 2 
    cycles = int(duration * frequency)
    
    for i in range(cycles):
        pin_1.on()
        pin_2.off()
        time.sleep(pulse_width)
        pin_2.on()
        pin_1.off()
        time.sleep(pulse_width)
    

def take_picture():
    print('Taking picture...')
    
    # Turn yellow while picture is being captured
    led.color = YELLOW
    
    # Notification sound
    play_tone(440, 0.25) # A4
    play_tone(220, 0.125) # A3
    play_tone(110, 0.0625) # A2
    
    local_time = time.localtime()
    timestamp_img = '{}.jpg'.format(time.asctime(local_time))
    
    # Grab the directory to save image from env variable.
    # If env variable isn't set, use current directory
    directory = os.environ["IMAGE_DIR"] or os.cwd()
    picam2.capture_file(os.path.join(directory, timestamp_img))
    led.off()
    print("Picture saved:", timestamp_img)


def print_latest_img():
    # Grab the directory to save image from env variable.
    # If env variable isn't set, use current directory
    directory = os.environ["IMAGE_DIR"] or os.cwd()
    files = os.listdir(directory)
    # Grab a a list of all jpeg image file paths
    images = [file for file in files if file.endswith('.jpg')]
    latest_img = max(images, key=os.path.getctime)
    
    print("Starting print job...")
    
    try:
        printer = Usb(idVendor=int(os.environ["VENDOR_ID"], 16),
                      idProduct=int(os.environ["PRODUCT_ID"], 16),
                      in_ep=int(os.environ["IN_EP"], 16),
                      out_ep=int(os.environ["OUT_EP"], 16),
                      profile="TM-T88V")
        
        # Show blue color to represent ongoing print job
        led.color = BLUE
        
        printer.image(latest_img)
        printer.cut()
        
    except Error as err:
        device_not_found = 90
        usb_not_found = 91
        
        traceback.print_exc()
        print(f'ERROR {err.resultcode}: {err.msg}')
        
        # Blink RGB LED 3 times for DeviceNotFoundError
        if err.resultcode == device_not_found:
            led.blink(on_color=RED)
            time.sleep(5)
            
        # Blink RGB LED 2 times for USBNotFoundError
        elif err.resultcode == usb_not_found:
            led.blink(on_color=RED)
            time.sleep(3)
            
        # For all other errors, make RGB LED red for 5 secs
        else:
            led.color = RED
            time.sleep(5)
        
        led.off()
        quit()
    
    print("Finished printing")
    printer.close()
    # Show green color for print success
    led.color = GREEN
    time.sleep(3)
    led.off()
    


def run():
    print('Running program...')
    
    # Create camera preview
    camera_config = picam2.create_preview_configuration(main={"size": (480, 360)})
    picam2.configure(camera_config)
    picam2.start_preview(Preview.QTGL)
    picam2.start()
    time.sleep(2)
    
    # Button to take and save a picture
    shutter_button = Button(6) 
    shutter_button.when_pressed = take_picture
    
    # Button to print latest image to thermal printer
    print_button = Button(24)
    print_button.when_pressed = print_latest_img
    
    pause()
    

if __name__ == '__main__':
    run()
