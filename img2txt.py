from PIL import Image
import math
import os
import time
import sys

block_elems = ['　', '▀', '▄', '█']

def pixel_check(a):
    return a[3] == 255


def check_white_opaque_pixels(image_path):
    img = Image.open(image_path).convert('RGBA')
    pixels = img.load()
    white_opaque = []
    space_count = 0

    isodd = 1 if img.height % 2 != 0 else 0
    
    for y in range(math.floor(img.height/2)+isodd):
        for x in range(img.width):
            cur_row = y * 2
            char_value = 0

            if pixel_check(pixels[x, cur_row]):
                char_value += 1
            if (cur_row + 1 != img.height) and pixel_check(pixels[x, cur_row + 1]):
                char_value += 2

            if char_value == 0:
                space_count += 1
            else:
                white_opaque.append(block_elems[0] * space_count)
                white_opaque.append(block_elems[char_value])
                space_count = 0
                
        white_opaque.append('\n')
        space_count = 0
    
    return white_opaque


def process_image(img_path):
    if not os.path.exists(img_path):
        print(f"File not found: '{img_path}'")
        return

    try:
        print(f"Processing image '{img_path}'...")
        starttime = round(time.time() * 1000)

        result = check_white_opaque_pixels(img_path)
        if result and result[-1] == '\n':
            result = result[:-1]
        cmdstr = ''.join(result)
        cmdstr = cmdstr.replace('　', ' ')
        if len(cmdstr) < 2000:
            print(cmdstr)

        output_path = os.path.splitext(img_path)[0]+"_txtoutput.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("<align=left><scale=0.5><line-height=15.5>")
            for coord in result:
                f.write(f"{coord}")
            
            charcount = sum(len(line) for line in result)
            print(f"Output saved to \"{output_path}\"")
            if charcount <= 16382:
                print("Copy all contents of the output file into a text object ingame.")
            print(f"\nCharacter count: {charcount:,}")
            if charcount > 16382:
                print("!!!!! Character count exceeds 16,382. Some pixels will be lost ingame. Consider resizing or cropping the image.")
            elif len(cmdstr) > 2000:
                print("Character count exceeds 2,000. Console preview has been skipped.")
            endtime = round(time.time() * 1000)
            print(f"Processing time: {endtime - starttime} ms")
    except Exception as e:
        print(f"Error processing '{img_path}': {e}")

if __name__ == "__main__":
    # If file(s) were passed as command-line arguments (e.g. drag-and-drop onto this .py file),
    # process each one. Otherwise, fall back to interactive prompt.
    if len(sys.argv) > 1:
        files = sys.argv[1:]
        for fpath in files:
            process_image(fpath)
    else:
        print("\n- Damian's Image Thing ngl-\n\n"
        "For best results\n"
        "• Use images that have only fully opaque white pixels or fully transparent pixels.\n"
        "• Trim any excess blank pixels around the image to reduce character count.\n"
        "Be sure to credit me if you use this tool!\n")
        img_path = input("Enter image path (with the extension): ")
        process_image(img_path)
        input("\nPress Enter to exit.")
