# -------------------------
# |    !!!!WARNING!!!!    |
# -------------------------
# This script irreversibly overwrites all of your 
# files recursively. Make sure you create a back up
# and put your files in an isolated folder.

# ------User-Defined Variables-------
# Directory to begin process:
start_directory = r'/Users/ninjacats/Documents/Notes/Journal/000-Encoding/project/test'
# Extra features
do_image_convert = False
image_convert_extension = '.jpg'
do_video_convert = False
video_convert_extension = '.mp4'

# ------Other Variables------
rtf_extensions = ('.rtf', '.RTF')
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

apple_image_extensions = ('.heic', '.HEIC', '.heics', '.HEICS', '.heif', '.HEIF', '.heif', '.heifs', '.hevc', '.HEVC')
imagemagick_command = [
    'magick',
    'source file (automatically generated)',
    'output file (automatically generated)'
]

apple_video_extensions = ('.mov', '.MOV')
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
    recursiveSearchRtf(start_directory)
    if do_image_convert or do_video_convert:
        recursiveSearchImageAndVideo(start_directory)
    print('Done!')

def recursiveSearchRtf(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        if file.endswith(rtf_extensions) and 'rtfd' in file_path:
            print(file_path)
            doRtfConversion(file_path)
            fixMdAttachments(file_path.split('.')[0] + '/' + file_path.split('.')[1].split('/')[1] + '.md')

        elif os.path.isdir(file_path):
            recursiveSearchRtf(file_path)

def recursiveSearchImageAndVideo(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
            
        # must only convert in former '.rtfd' directories
        # this means directory will have 'TXT.md'
        former_rtfd_directory = False
        for file2 in os.listdir(directory):
            if file2 == 'TXT.md':
                former_rtfd_directory = True

        if former_rtfd_directory:
            if file.endswith(apple_image_extensions) and do_image_convert:
                print(file_path)
                doImageConversion(file_path, file)
                fixImageAttachments(os.path.dirname(file_path) + '/TXT.md', file)

            elif file.endswith(apple_video_extensions) and do_video_convert:
                print(file_path)
                doVideoConversion(file_path, file)
                fixVideoAttachments(os.path.dirname(file_path) + '/TXT.md', file)

        if os.path.isdir(file_path):
            recursiveSearchImageAndVideo(file_path)

def doRtfConversion(rtf_path):
    os.chdir(os.path.dirname(rtf_path))
    # set source file in command
    pandoc_command[1] = rtf_path
    # set output file in command
    # FIX!!!!! deliberately named TXT.md for recursiveSearchImageAndVideo function
    pandoc_command[7] = os.path.dirname(rtf_path) + '/TXT.md'
    print(pandoc_command[7])
    # perform conversion to markdown using pandoc
    subprocess.run(pandoc_command)
    # remove rtf file
    os.remove(rtf_path)
    # remove '.rtfd' from enclosing folder
    os.rename(os.path.dirname(rtf_path), os.path.dirname(rtf_path).split('.')[0])

def fixMdAttachments(md_path):
    with open(md_path, 'r') as f:
        data = f.readlines()

    for (index, line) in enumerate(data):
        # '¬' denotes a file attachment in rtfd when
        # converted to markdown
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
    # ![ATTACHMENT: grand haven.HIEC](grand%20haven.HEIC) 
    # CONVERT TO:   
    # ![ATTACHMENT: grand haven.jpg](grand%20haven.jpg)
    # FIX!!! Must be FULL file name
    # FIX!!!! this so it works when there is '%20'
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
    ffmpeg_command[3] = video_path.split('.')[0] + video_convert_extension
    # perform encoding with ffmpeg
    subprocess.run(ffmpeg_command)
    # remove renamed original video
    os.remove('renamed-' + video)

def fixVideoAttachments(md_path, video):
    with open(md_path, 'r') as f:
        data = f.readlines()

    # Example:
    # CONVERT FROM: 
    # ![ATTACHMENT: grand haven.MOV](grand%20haven.MOV) 
    # CONVERT TO:   
    # ![ATTACHMENT: grand haven.mp4](grand%20haven.mp4)
    for (index, line) in enumerate(data):
        updated_line = line.replace(video, video.split('.')[0] + video_convert_extension)
        # in cases where '%20' is used
        video_20 = '%20'.join(video.split(' '))
        data[index] = updated_line.replace(video_20, video_20.split('.')[0] + video_convert_extension)     

    with open(md_path, 'w') as f:
        f.writelines(data)

if __name__ == '__main__':
    main()
