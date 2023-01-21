# ------User-Defined Variables-------
# Directory to begin process:
start_directory = r''
# Directory to put converted files:
conversion_directory = r''
# Extra features
do_image_convert = False
image_convert_extension = '.jpg'
do_video_convert = False
video_convert_extension = '.mp4'

# ------Other Variables------
pandoc_command = [
    'pandoc',
    'input path (automatically generated, do not edit)',
    '-f',
    'rtf',
    '-t',
    'gfm',
    '-o',
    'output path (automatically generated, do not edit)'
]

# FIX!!! hevc can be both image or video??
apple_image_codecs = ['heif', 'heic']
imagemagick_command = [
    'magick',
    'input path (automatically generated, do not edit)',
    'output path (automatically generated, do not edit)'
]
identify_command = [
    'identify',
    '-format',
    '\'%m\'',
    'input path (automatically generated, do not edit)'
]

apple_video_codecs = ['aac', 'prores', 'aic', 'avc-intra']
ffmpeg_command = [
    'ffmpeg',
    '-i',
    'input path (automatically generated, do not edit)',
    'output path (automatically generated, do not edit)'
]
ffprobe_command = [
    'ffprobe',
    '-v',
    'error',
    '-select_streams',
    'a:0',
    '-show_entries',
    'stream=codec_name',
    '-of',
    'default=nw=1',
    'input path (automatically generated, do not edit)'
]

# -----Begin Program-----
import subprocess
import os
import shutil
import copy

def main():
    if not os.path.isdir(start_directory):
        raise ValueError('start_directory is not a valid directory')

        if os.path.abspath(start_directory) == os.path.abspath(conversion_directory):
            raise ValueError('start_directory and conversion_directory are the same directory')

            if os.path.exists(conversion_directory):
                raise ValueError('conversion_directory already exists')

            else:
                shutil.copytree(start_directory, conversion_directory)
                doRecursion(conversion_directory)
                print('Done!')


def doRecursion(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        if os.path.isdir(file_path) and file_path.lower().endswith('.rtfd'):
            print('-----FOUND .RTFD DIRECTORY-----\n' + file_path)
            convertRtfdDirectory(file_path)
            # rename .rtfd directory to remove '.rtfd'
            # FIX!!! what if directory/file WITHOUT '.rtfd' already exists?
            os.rename(file_path, file_path.replace('.rtfd', ''))

        elif os.path.isdir(file_path):
            doRecursion(file_path)

def convertRtfdDirectory(rtfd_directory):
    # .rtf file must be converted first because fixing .md attachments requires a converted .md file
    for file in os.listdir(rtfd_directory):
        file_path = os.path.join(rtfd_directory, file)
        md_path = os.path.join(rtfd_directory, 'TXT.md')

        if file.lower().endswith('.rtf'):
            print('CONVERTING RTF: ', file)
            doFileConversion(file_path, pandoc_command, '.md')
            fixMdAttachmentSyntax(md_path)

    # now that the .rtf file is converted, convert images and videos
    if do_image_convert or do_video_convert:
        for file in os.listdir(rtfd_directory):
            file_path = os.path.join(rtfd_directory, file)
            md_path = os.path.join(rtfd_directory, 'TXT.md')

            if do_image_convert and fileHasAppleCodec(file_path, identify_command, apple_image_codecs):
                print('CONVERTING IMAGE: ', file)
                doFileConversion(file_path, imagemagick_command, image_convert_extension)
                fixMdAttachmentFilenames(md_path, file, image_convert_extension)
                continue

            if do_video_convert and fileHasAppleCodec(file_path, ffprobe_command, apple_video_codecs):
                print("CONVERTING VIDEO: ", file)
                doFileConversion(file_path, ffmpeg_command, video_convert_extension)
                fixMdAttachmentFilenames(md_path, file, video_convert_extension)    

# doFileConversion: uses 'pandoc', 'magick', or 'ffmpeg' to convert files
# 'command' parameter can be either pandoc_command, imagemagick_command, or ffmpeg_command
# 'extension' parameter can be either image_convert_extension or video_convert_extension
def doFileConversion(file_path, command, extension):
    # create copy of command (because it is passed by reference)
    local_command = copy.deepcopy(command)

    # setting up variables for readability
    file = os.path.basename(file_path)
    file_directory = os.path.dirname(file_path)

    # rename file to prevent errors if the input and output filenames are the same
    os.chdir(file_directory)
    os.rename(file, 'renamed-' + file)

    # find indices of 'input path' and 'output path' in command
    input_path_index = 0
    output_path_index = 0
    for (index, parameter) in enumerate(local_command):
        if parameter.startswith('input path'):
            input_path_index = index
        elif parameter.startswith('output path'):
            output_path_index = index

    # set 'input path' to renamed file and 'output path' to file with new extension
    local_command[input_path_index] = os.path.join(file_directory, 'renamed-' + file)
    local_command[output_path_index] = os.path.join(file_directory, file.split('.')[0] + extension)

    # perform CLI command
    output = subprocess.run(local_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if output.returncode != 0:
        raise Exception(output.stderr.decode())

    # remove renamed file
    os.remove('renamed-' + file)

# fixMdAttachmentSyntax: update the syntax of each line denoting a file attachment to match .md syntax
# '¬' denotes a file attachment when .rtf is converted to .md
# example:
# CONVERT FROM: 
# grand haven.jpg ¬   
# CONVERT TO:   
# ![ATTACHMENT: grand haven.jpg](grand%20haven.jpg)
def fixMdAttachmentSyntax(md_path):
    with open(md_path, 'r') as f:
        data = f.readlines()

    for (index, line) in enumerate(data):
        # FIX!!! what is the user is using the '¬' character in other places?
        if '¬' in line:
            file_name = line.split('¬')[0].strip()
            file_name = '%20'.join(file_name.split(' '))
            alt_text = '![ATTACHMENT: ' + line.split('.')[0] + '.' + line.split('.')[1].split(' ')[0] + ' ]'
            updated_line = alt_text + '(' + file_name + ')'
            data[index] = updated_line

    with open(md_path, 'w') as f:
        f.writelines(data)

# fixMdAttachmentFilenames: update each line that contains filename with filename that has new extension
# example:
# CONVERT FROM: 
# ![grand haven.HEIC](grand%20haven.HEIC) 
# CONVERT TO:   
# ![grand haven.jpg](grand%20haven.jpg)
def fixMdAttachmentFilenames(md_path, file, extension):
    with open(md_path, 'r') as f:
        data = f.readlines()

    for (index, line) in enumerate(data):
        updated_line = line.replace(file, file.split('.')[0] + extension)
        # in cases where '%20' is used
        file_20 = '%20'.join(file.split(' '))
        updated_line = updated_line.replace(file_20, file_20.split('.')[0] + extension) 
        data[index] = updated_line

    with open(md_path, 'w') as f:
        f.writelines(data)

# fileHasAppleCodec: uses 'identify' (imagemagick) and 'ffprobe' (ffmpeg) to find image and video codecs
# 'command' parameter can be either identify_command or ffprobe_command
# 'codecs' parameter can be either apple_image_codecs or apple_video_codecs
def fileHasAppleCodec(file_path, command, codecs):
        # create copy of command (because it is passed by reference)
        local_command = copy.deepcopy(command)

        # find index of 'input path' in command and set that index to file_path
        input_path_index = 0
        for (index, parameter) in enumerate(local_command):
            if parameter.startswith('input path'):
                input_path_index = index
        local_command[input_path_index] = file_path

        # perform CLI command
        output = subprocess.run(local_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode != 0:
            raise Exception(output.stderr.decode())

        # check if codec of file matches an apple codec
        for codec in codecs:
            if codec in output.stdout.decode().lower():
                return True
        return False

if __name__ == '__main__':
    main()
