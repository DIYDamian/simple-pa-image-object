from PIL import Image
import math
import os
import time
import sys
import random
import json

block_elems = ['　', '▀', '▄', '█']
filler_elems = ['░', '░', '▒']
optimized_space_width = 8.16
error_count = 0;

default_config = {
    "output_name_suffix": "_txtoutput",
    "cspace_addition": 0,
    "line_height_addition": 0,
    "horizontal_scale": 1,
    "space_tag_optimization": True,
    "use_filler": False,
    "filler_string": "░░▒"
}

config = default_config.copy()
def get_base_dir():
    # When bundled with PyInstaller use the exe folder, otherwise use the script folder
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def load_config():
    try:
        cfg_path = os.path.join(get_base_dir(), "img2txt_config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as fh:
                user_cfg = json.load(fh)
                if isinstance(user_cfg, dict):
                    for k, v in user_cfg.items():
                        if k in config and v is not None:
                            config[k] = v
        else:
            print(f"Creating config file at '{cfg_path}'...")
            rewrite_config()
    except Exception as e:
        print(f"Warning: failed to load config '{cfg_path}': {e}")
        try:
            do_rewrite = input(f"Using default config. Would you like to rewrite the config file using default parameters? (y/n): ")
        except Exception:
            do_rewrite = "n"
        if do_rewrite.lower() == "y":
            print(f"Recreating config file at '{os.path.join(get_base_dir(), 'img2txt_config.json')}'...")
            rewrite_config()

    if config.get("filler_string") is None:
        config["filler_string"] = default_config["filler_string"]

def pixel_check(a):
    return a[3] == 255


def check_white_opaque_pixels(image_path):
    img = Image.open(image_path).convert('RGBA')
    pixels = img.load()
    white_opaque = []
    space_count = 0

    use_filler = config.get("use_filler", False)
    space_tag_optimization = config.get("space_tag_optimization", True)
    filler_string = config.get("filler_string", "░░▒")

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
                if not use_filler:
                    space_count += 1
                else:
                    white_opaque.append(random.choice(filler_string))
            else:
                if not use_filler:
                    if space_count > 14 and space_tag_optimization:
                        white_opaque.append("<space=" + str(  round(space_count*optimized_space_width*(config["horizontal_scale"]), 2)  ) + ">")
                    else:
                        white_opaque.append(block_elems[0] * space_count)
                else:
                    for x in range(space_count):
                        white_opaque.append(filler_elems[random.randint(0, len(filler_elems) - 1)])
                white_opaque.append(block_elems[char_value])
                space_count = 0
                
        white_opaque.append('\n')
        space_count = 0
    
    return white_opaque

def process_image(img_path, dragged=False):
    global error_count
    if not os.path.exists(img_path):
        print(f"File not found: '{img_path}'")
        return

    try:
        if not dragged:
            print(f"Processing image '{img_path}'...")
        starttime = round(time.time() * 1000)

        result = check_white_opaque_pixels(img_path)
        shortname = os.path.basename(img_path)
        if result and result[-1] == '\n':
            result = result[:-1]
        cmdstr = ''.join(result)
        cmdstr = cmdstr.replace('　', ' ')
        if dragged:
            if len(cmdstr) < 1000:
                print(f"Output for '{shortname}':\n{cmdstr}")
            else:
                print(f"Output for '{shortname}':\nPreview skipped.")
        elif len(cmdstr) < 2000:
            print(cmdstr)

        output_path = os.path.splitext(img_path)[0] + config["output_name_suffix"] + ".txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("<align=left>")
            if config["horizontal_scale"] != 2:
                f.write(f"<scale={config['horizontal_scale']*0.5}>")
            f.write(f"<line-height={15.5+config['line_height_addition']}>")
            if config["cspace_addition"] != 0:
                f.write(f"<cspace={config['cspace_addition']}>")
            for coord in result:
                f.write(f"{coord}")
            
            charcount = sum(len(line) for line in result)
            print(f"Output saved to '{os.path.basename(output_path)}'")
            if charcount <= 16382 and not dragged:
                print("Copy all contents of the output file into a text object ingame.")
            if not dragged:
                print(f"\nCharacter count: {charcount:,}")
            else:
                print(f"Character count: {charcount:,}\n")
            if charcount > 16382:
                print("!!!!! Character count exceeds 16,382. Some pixels will be lost ingame. Consider resizing or cropping the image.")
                error_count += 1
            elif len(cmdstr) > 2000 and not dragged:
                print("Character count exceeds 2,000. Console preview has been skipped.")
            endtime = round(time.time() * 1000)
            if not dragged:
                print(f"Processing time: {endtime - starttime} ms")
    except Exception as e:
        print(f"Error processing '{img_path}': {e}")
        if dragged:
            print("")
            error_count += 1

def rewrite_config():
    # If config is messed up or doesn't exist, rewrite it with current values
    cfg_path = os.path.join(get_base_dir(), "img2txt_config.json")
    with open(cfg_path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=4, ensure_ascii=False)

# Load config once at import so both CLI and GUI use same settings/path
load_config()

if __name__ == "__main__":
    print("- Damian's Image Thing ngl-\n\n"
    "For best results\n"
    "• Use images that have only fully opaque white pixels or fully transparent pixels.\n"
    "• Trim any excess blank pixels around the image to reduce character count.\n"
    "Be sure to credit me if you use this tool!\n")
    if len(sys.argv) > 1:
        starttime = round(time.time() * 1000)
        files = sys.argv[1:]
        for fpath in files:
            process_image(fpath, dragged=True)
        print(f"Processing complete.\nConverted {len(files)-error_count} image(s).")
        if error_count > 0:
            print(f"!!!!! Warning: {error_count} file(s) had issues.")
        endtime = round(time.time() * 1000)
        print(f"Processing time: {endtime - starttime} ms")
        input("\nPress Enter to exit.")
    else:
        img_path = input("Enter image path (with the extension): ")
        load_config()
        process_image(img_path)
        rewrite_config()
        input("\nPress Enter to exit.")
