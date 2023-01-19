# RTFD-to-MD-Converter

## Guide
Set the user-defined variables and run the script.

Required command line programs:
- pandoc
- imagemagick
- ffmpeg
- ffprobe
- identify

## Description
Converts Apple .rftd directories to Github Markdown (preserving file attachments) from a selected folder recursively. Converted .md file will be named 'TXT.md' in a directory with the same name as the .rtfd directory and with attachment files, identical to an .rftd directory. Note that most .rtf formatting will be erased. 

Two extra features:
- Convert Apple encoded images to a file extension of your choice
- Convert Apple encoded videos to a file extension of your choice

This allows for greater compatibility.

Note: Only converts files (rtf files, images, and videos) that are found in .rtfd directories.
