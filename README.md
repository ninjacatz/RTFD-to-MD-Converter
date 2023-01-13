# RTFD-to-MD-Converter

## Guide
Fill in the user-defined variables and run the script.

Required command line programs:
- pandoc
- imagemagick
- ffmpeg

WARNING: Only works on macOS and Linux (for now).

## Description
Converts Apple .rftd directories to Github Markdown (preserving file attachments) from a selected folder recursively. Converted .md file will be named 'TXT.md' in a folder with the same name as the .rtfd directory and with attachment files, identical to an .rftd directory. Note that most .rtf formatting will be erased. 

Two extra features:
- Convert Apple .HEIC images to a file extension of your choice
- Convert Apple .MOV videos to a file extension of your choice

This allows for greater compatibility.

Note: Only converts files (rtf, images, and videos) that are found in .rtfd directories.
