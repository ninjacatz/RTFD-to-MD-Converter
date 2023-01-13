# ------README------
# Converts Apple .rftd directories to Github Markdown
# (preserving file attachments) from a selected
# folder recursively. Utilizes pandoc .rtf to .md
# conversion. Converted file will be named 'TXT.md'
# in a folder with attachment files, identical to an
# .rftd directory. Only .rtf files found in .rtfd 
# directories will be converted to .md. Note that
# most .rtf formatting will be erased. 
#
# Two extra features convert Apple .HEIC images
# to a file extension of your choice utilizing 
# imagemagick, and remove Apple's codec from
# .mov videos to a file extension of your 
# choice utilizing HandbrakeCLI (but this 
# also converts non-Apple .mov videos). 
# This makes Apple images and videos viewable
# with Github Markdown. Only images and videos
# found in .rtfd directories are converted.
#
# NOTE: Only works on Unix (no Windows for now)

# -------------------------
# |    !!!!WARNING!!!!    |
# -------------------------
# This script irreversibly overwrites all of your 
# files recursively. Make sure you create a back up
# and put your files in an isolated folder.

# ------User-Defined Variables-------
# Directory to begin process:
start_directory = r'/Users/ninjacats/Downloads/all'
# Extra features
do_image_convert = True
image_convert_to = '.jpg'
do_video_convert = False
video_convert_to = '.mp4'
# HandBrakeCLI executable required for video convert
handbrakeCLI_path = r'/Users/ninjacats/Documents/Journal/000-Encoding/HandBrakeCLI'

# ------Other Variables------
rtf_extensions = ('.rtf', '.RTF')
pandoc_command = [
    'pandoc',
    'source file (automatically generated)',
    '-f', # from
    'rtf', # rtf
    '-t', # to
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
handbrake_command = [
    handbrakeCLI_path,
    '-i',
    'source file (automatically generated)',
    '-o',
    'output file (automatically generated)'
]

# -----Begin Program-----
import subprocess
import os

def main():
    doRecursionRtf(start_directory)
    if do_image_convert or do_video_convert:
        doRecursionImageAndVideo(start_directory)

    print('Done!')

def doRecursionRtf(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        if file.endswith(rtf_extensions) and 'rtfd' in file_path:
            print(file_path)
            converted_md_path = file_path.split('.')[0] + '/' + file_path.split('.')[1].split('/')[1] + '.md'
            doRtfConversion(file_path)
            fixMdAttachments(converted_md_path)

        elif os.path.isdir(file_path):
            doRecursionRtf(file_path)

def doRecursionImageAndVideo(directory):
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
                converted_md_path = doHeicConversion(file_path, file)
                fixMdHeicAttachments(converted_md_path)

            elif file.endswith(apple_video_extensions) and do_video_convert:
                print(file_path)
                converted_md_path = doMovConversion(file_path, file)
                fixMdMovAttachments(converted_md_path)

        if os.path.isdir(file_path):
            doRecursionImageAndVideo(file_path)

def doRtfConversion(rtf_path):
    os.chdir(os.path.dirname(rtf_path))
    # set source file in command
    pandoc_command[1] = rtf_path
    # set output file in command
    pandoc_command[7] = os.path.splitext(rtf_path)[0] + '.md'
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

def doHeicConversion(image_path, image):
    os.chdir(os.path.dirname(image_path))
    # rename original image
    os.rename(image, 'renamed-' + image)
    # set renamed video as source file
    imagemagick_command[1] = os.path.join(os.path.dirname(image_path), 'renamed-' + image)
    # set original image name as destination file
    # with chosen extension
    imagemagick_command[2] = os.path.join(os.path.dirname(image_path), image.split('.')[0] + image_convert_to)
    # perform encoding with imagemagick
    subprocess.run(imagemagick_command)
    # remove renamed image
    os.remove('renamed-' + image)
    # return 'TXT.md' with new folder
    # name for fixMdHeicAttachments function
    return os.path.dirname(image_path) + '/TXT.md'

def fixMdHeicAttachments(md_path):
    data = ''
    with open(md_path, 'r') as f:
        data = f.read()
        # Example:
        # CONVERT FROM: 
        # ![alt text](grand%20haven.HEIC) 
        # CONVERT TO:   
        # ![alt text](grand%20haven.jpg)
        for extension in apple_image_extensions:
            data = data.replace(extension, image_convert_to)

    with open(md_path, 'w') as f:
        f.write(data)

def doMovConversion(video_path, video):
    os.chdir(os.path.dirname(video_path))
    # rename original video
    os.rename(video, "renamed-" + video)
    # set renamed video as source file
    handbrake_command[2] = os.path.join(os.path.dirname(video_path), 'renamed-' + video)
    # set original video as output with extension
    handbrake_command[4] = video_path.split('.')[0] + video_convert_to
    # perform encoding with HandBrakeCLI
    subprocess.run(handbrake_command)
    # remove renamed original video
    os.remove('renamed-' + video)
    # return 'TXT.md' with new folder
    # name for fixMdMovAttachments function
    return os.path.dirname(video_path) + '/TXT.md'

def fixMdMovAttachments(md_path):
    data = ''
    with open(md_path, 'r') as f:
        data = f.readlines()

    for extension in apple_video_extensions:
        for (index, line) in enumerate(data):
            # Example:
            # CONVERT FROM: 
            # ![alt text](grand%20haven.mov) 
            # CONVERT TO:   
            # ![alt text](grand%20haven.mp4)
            if extension in line:
                updated_line = line.replace(extension, video_convert_to)
                data[index] = updated_line

    with open(md_path, 'w') as f:
        f.writelines(data)

if __name__ == '__main__':
    main()