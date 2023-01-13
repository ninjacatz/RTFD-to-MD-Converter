# RTFD-to-MD-Converter

## Guide
Fill in the user-defined variables and run the script.

Required command line programs:
- pandoc
- imagemagick
- ffmpeg

WARNING: Only works on macOS and Linux (for now).

# Description
Converts Apple .rftd directories to Github Markdown (preserving file attachments) from a selected folder recursively. Converted .md file will be named 'TXT.md' in a folder with the same name as the .rtfd directory and with attachment files, identical to an .rftd directory. Note that most .rtf formatting will be erased. 

Two extra features convert Apple .HEIC images to a file extension of your choice, and remove Apple's codec from .mov videos to a file extension of your choice utilizing HandbrakeCLI (but this also converts non-Apple .mov videos). This makes Apple images and videos more compatible with a variety of applications.

Note: Only converts files (rtf, images, and videos) that are found in .rtfd directories.
