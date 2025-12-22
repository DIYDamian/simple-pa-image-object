# Damian's Image Thing ngl
This is a simple tool used to recreate simple one-color images into text objects for use in Project Arrhythmia.
## How to use
Download the executable from the releases tab on the side.
### Drag 'n' Drop
Just drag your image(s) onto the executable and it'll do all the work for you using your current configuration.
## Config
The code reads from `img2txt_config.json` to change certain properties of the output. If this file doesn't exist, it'll be created when starting the program.
- **`output_name_suffix`** - Changes the suffix of outputted text files. For example, if `my_image.png` is put in the program and this value is `_txtoutput`, the resulting file will be named `my_image_txtoutput.txt`. (Default: "_txtoutput")
- **`cspace_addition`** - If not zero, adds a \<cspace> tag with this value, adjusting horizontal spacing between characters. (Default: 0)
- **`line_height_addition`** - Adds to the \<line-height> tag's value, adjusting vertical spacing between characters. (Default: 0)
- **`horizontal_scale`** - Adjusts the \<scale> tag at the start.  (Default: 1)
- **`space_tag_optimization`** - Experimental. Replaces large continuous spaces with a \<space> tag whenever it'd reduce the object's character count.  (Default: True)
- **`use_filler`** - If true, all blank spaces in the output will be replaced with random characters from the **`filler_string`**. Useful for text when going for the default Project Arrhythmia ASCII font look. If enabled, `space_tag_optimization` will be ignored. (Default: False)