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
    'markdown',
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
    if os.path.isdir(start_directory):
        if not os.path.abspath(start_directory) == os.path.abspath(conversion_directory):
            if not os.path.exists(conversion_directory):
                shutil.copytree(start_directory, conversion_directory)
                doRecursion(conversion_directory)
                print('Done!')
            else:
                raise ValueError('conversion_directory already exists')
        else:
            raise ValueError('start_directory and conversion_directory are the same directory')
    else:
        raise ValueError('start_directory is not a valid directory')

def doRecursion(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        if os.path.isdir(file_path) and file_path.lower().endswith('.rtfd'):
            print('-----FOUND .RTFD DIRECTORY-----\n' + file_path)

            # .rtf file must be converted first because fixing .md attachments requires a converted .md file
            for rtfd_file in os.listdir(file_path):
                rtfd_file_path = os.path.join(file_path, rtfd_file)
                md_path = os.path.join(os.path.dirname(rtfd_file_path), 'TXT.md')

                if rtfd_file.lower().endswith('.rtf'):
                    print('CONVERTING RTF: ', rtfd_file)
                    doFileConversion(rtfd_file_path, pandoc_command, '.md')
                    fixMdAttachments(md_path)

            # now that the .rtf file is converted, convert images and videos
            if do_image_convert or do_video_convert:
                for rtfd_file in os.listdir(file_path):
                    rtfd_file_path = os.path.join(file_path, rtfd_file)
                    md_path = os.path.join(os.path.dirname(rtfd_file), 'TXT.md')

                    if decodeFile(rtfd_file_path, identify_command, apple_image_codecs) and do_image_convert:
                        print('CONVERTING IMAGE: ', rtfd_file)
                        doFileConversion(rtfd_file_path, imagemagick_command, image_convert_extension)
                        fixMdAttachments(md_path, rtfd_file, image_convert_extension)
                        continue

                    if decodeFile(rtfd_file_path, ffprobe_command, apple_video_codecs) and do_video_convert:
                        print("CONVERTING VIDEO: ", rtfd_file)
                        doFileConversion(rtfd_file_path, ffmpeg_command, video_convert_extension)
                        fixMdAttachments(md_path, rtfd_file, video_convert_extension)

            # rename .rtfd directory to remove '.rtfd'
            # FIX!!! what if directory/file WITHOUT '.rtfd' already exists?
            os.rename(file_path, file_path.replace('.rtfd', ''))

        elif os.path.isdir(file_path):
            doRecursion(file_path)

def doFileConversion(file_path, command, extension):
    local_command = copy.deepcopy(command)
    input_path_index = 0
    output_path_index = 0
    for (index, parameter) in enumerate(local_command):
        if parameter.startswith('input path'):
            input_path_index = index
        elif parameter.startswith('output path'):
            output_path_index = index
    file = os.path.basename(file_path)
    file_directory = os.path.dirname(file_path)

    os.chdir(file_directory)
    os.rename(file, 'renamed-' + file)
    local_command[input_path_index] = os.path.join(file_directory, 'renamed-' + file)
    local_command[output_path_index] = os.path.join(file_directory, file.split('.')[0] + extension)
    output = subprocess.run(local_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if output.returncode != 0:
        raise Exception(output.stderr.decode())
    os.remove('renamed-' + file)

def fixMdAttachments(md_path, file = None, extension = None):
    with open(md_path, 'r') as f:
        data = f.readlines()

    for (index, line) in enumerate(data):
        # THIS IF STATEMENT IS TRIGGERED WHEN .rtf IS FIRST CONVERTED TO .md (and only 1 parameter is sent to function)
        #
        # '¬' denotes a file attachment in .rtf when converted to .md
        #
        # CONVERT FROM: 
        # grand haven.jpg ¬   
        # CONVERT TO:   
        # ![alt text](grand%20haven.jpg)
        # FIX!!! what is the user is using the '¬' character in other places?
        if ' ¬' in line:
            file_name = line.split('¬')[0].strip()
            file_name = '%20'.join(file_name.split(' '))
            alt_text = '![ATTACHMENT: ' + line.split('.')[0] + '.' + line.split('.')[1].split(' ')[0] + ' ]'
            updated_line = alt_text + '(' + file_name + ')'
            data[index] = updated_line
        elif file is not None and extension is not None:
            # THIS ELIF STATEMENT FIXES FILE NAMES (if function is given 2nd & 3rd parameters)
            #
            # Example:
            # CONVERT FROM: 
            # ![grand haven.HEIC](grand%20haven.HEIC) 
            # CONVERT TO:   
            # ![grand haven.jpg](grand%20haven.jpg)
            updated_line = line.replace(file, file.split('.')[0] + extension)
            # in cases where '%20' is used
            file_20 = '%20'.join(file.split(' '))
            data[index] = updated_line.replace(file_20, file_20.split('.')[0] + extension) 

    with open(md_path, 'w') as f:
        f.writelines(data)

def decodeFile(file_path, command, codecs):
    try:
        local_command = copy.deepcopy(command)
        input_path_index = 0
        for (index, parameter) in enumerate(local_command):
            if parameter.startswith('input path'):
                input_path_index = index

        local_command[input_path_index] = file_path
        output = subprocess.run(local_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode != 0:
            raise Exception(output.stderr.decode())

        for codec in codecs:
            if codec in output.stdout.decode().lower():
                return True
        return False

    except:
        print('Could not decode file \'' + os.path.basename(file_path) + '\' with ' + local_command[0])

if __name__ == '__main__':
    main()
