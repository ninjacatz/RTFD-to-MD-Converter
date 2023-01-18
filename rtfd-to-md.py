# -------------------------
# |    !!!!WARNING!!!!    |
# -------------------------
# This script irreversibly overwrites all of your 
# files recursively. Make sure you create a back up
# and put your files in an isolated folder.

# ------User-Defined Variables-------
# Directory to begin process:
start_directory = r''
# Extra features
do_image_convert = False
image_convert_extension = '.jpg'
do_video_convert = False
video_convert_extension = '.mp4'

# ------Other Variables------
pandoc_command = [
    'pandoc',
    'source file (automatically generated)',
    '-f',
    'rtf',
    '-t',
    'gfm', # github markdown
    '-o',
    'output file (automatically generated)'
]

apple_image_extensions = ('.heic', '.heif')
imagemagick_command = [
    'magick',
    'source file (automatically generated)',
    'output file (automatically generated)'
]

apple_video_extensions = ('.mov', '.hevc')
ffmpeg_command = [
    'ffmpeg',
    '-i',
    'source file path(will be known, do not change)',
    'destination path(will be known, do not change)'
]

# -----Begin Program-----
import subprocess
import os

def main():
    recursiveSearch(start_directory)
    print('Done!')

def recursiveSearch(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        if os.path.isdir(file_path) and file_path.lower().endswith('.rtfd'):
            # .rtf file must be converted first because fixing .md attachments requires a converted .md file
            for rtfd_file in os.listdir(file_path):
                rtfd_file_path = os.path.join(file_path, rtfd_file)
                md_path = os.path.join(os.path.dirname(rtfd_file_path), 'TXT.md')

                if rtfd_file.lower().endswith('.rtf'):
                    print('RTF TO CONVERT: ', rtfd_file_path)
                    doRtfConversion(rtfd_file_path)
                    # BUG!!! because md_path is the 'TXT.md' file only, it ignores any other .rtf files
                    fixMdAttachments(md_path)

            # now that the .rtf file is converted, convert images and videos
            if do_image_convert or do_video_convert:
                for rtfd_file in os.listdir(file_path):
                    rtfd_file_path = os.path.join(file_path, rtfd_file)
                    md_path = os.path.join(os.path.dirname(rtfd_file), 'TXT.md')

                    if rtfd_file.lower().endswith(apple_image_extensions) and do_image_convert:
                        print('IMAGE TO CONVERT: ', rtfd_file_path)
                        doImageConversion(rtfd_file_path, rtfd_file)
                        fixImageAttachments(md_path, rtfd_file)

                    if rtfd_file.lower().endswith(apple_video_extensions) and do_video_convert:
                        print("VIDEO TO CONVERT: ", rtfd_file_path)
                        doVideoConversion(rtfd_file_path, rtfd_file)
                        fixVideoAttachments(md_path, rtfd_file)

            # rename .rtfd directory to remove '.rtfd'
            os.rename(file_path, file_path.replace('.rtfd', ''))

        elif os.path.isdir(file_path):
            recursiveSearch(file_path)

def doRtfConversion(rtf_path):
    # BUG!!! what if .rtf file is not named 'TXT.rtf'? (example: there are multiple .rtf files in the .rtfd directory, or the user manually renamed the file)
    os.chdir(os.path.dirname(rtf_path))
    # set source file in command
    pandoc_command[1] = rtf_path
    # set output file in command
    pandoc_command[7] = os.path.join(os.path.dirname(rtf_path), 'TXT.md')
    # perform conversion to markdown using pandoc
    subprocess.run(pandoc_command)
    # remove rtf file
    os.remove(rtf_path)

def fixMdAttachments(md_path):
    with open(md_path, 'r') as f:
        data = f.readlines()

    for (index, line) in enumerate(data):
        # '¬' denotes a file attachment in .rtf when converted to .md
        #
        # CONVERT FROM: 
        # grand haven.jpg ¬   
        # CONVERT TO:   
        # ![alt text](grand%20haven.jpg)
        if '¬' in line:
            file_name = line.split('¬')[0].strip()
            file_name = '%20'.join(file_name.split(' '))
            alt_text = '![ATTACHMENT: ' + line.split('.')[0] + '.' + line.split('.')[1].split(' ')[0] + ' ]('
            updated_line = alt_text + file_name + ')'
            data[index] = updated_line

    with open(md_path, 'w') as f:
        f.writelines(data)

def doImageConversion(image_path, image):
    os.chdir(os.path.dirname(image_path))
    # rename original image
    os.rename(image, 'renamed-' + image)
    # set renamed video as source file
    imagemagick_command[1] = os.path.join(os.path.dirname(image_path), 'renamed-' + image)
    # set original image name as destination file
    # with chosen extension
    imagemagick_command[2] = os.path.join(os.path.dirname(image_path), image.split('.')[0] + image_convert_extension)
    # perform encoding with imagemagick
    subprocess.run(imagemagick_command)
    # remove renamed image
    os.remove('renamed-' + image)

def fixImageAttachments(md_path, image):
    with open(md_path, 'r') as f:
        data = f.readlines()

    # Example:
    # CONVERT FROM: 
    # ![grand haven.HEIC](grand%20haven.HEIC) 
    # CONVERT TO:   
    # ![grand haven.jpg](grand%20haven.jpg)
    for (index, line) in enumerate(data):
        updated_line = line.replace(image, image.split('.')[0] + image_convert_extension)
        # in cases where '%20' is used
        image_20 = '%20'.join(image.split(' '))
        data[index] = updated_line.replace(image_20, image_20.split('.')[0] + image_convert_extension)     

    with open(md_path, 'w') as f:
        f.writelines(data)

def doVideoConversion(video_path, video):
    os.chdir(os.path.dirname(video_path))
    # rename original video
    os.rename(video, "renamed-" + video)
    # set renamed video as source file
    ffmpeg_command[2] = os.path.join(os.path.dirname(video_path), 'renamed-' + video)
    # set original video name as destination
    ffmpeg_command[3] = os.path.join(os.path.dirname(video_path), video.split('.')[0] + video_convert_extension)
    # perform encoding with imagemagick
    # perform encoding with ffmpeg
    subprocess.run(ffmpeg_command)
    # remove renamed original video
    os.remove('renamed-' + video)

def fixVideoAttachments(md_path, video):
    with open(md_path, 'r') as f:
        data = f.readlines()

    # Example:
    # CONVERT FROM: 
    # ![grand haven.MOV](grand%20haven.MOV) 
    # CONVERT TO:   
    # ![grand haven.mp4](grand%20haven.mp4)
    for (index, line) in enumerate(data):
        updated_line = line.replace(video, video.split('.')[0] + video_convert_extension)
        # in cases where '%20' is used
        video_20 = '%20'.join(video.split(' '))
        data[index] = updated_line.replace(video_20, video_20.split('.')[0] + video_convert_extension)     

    with open(md_path, 'w') as f:
        f.writelines(data)

if __name__ == '__main__':
    main()
