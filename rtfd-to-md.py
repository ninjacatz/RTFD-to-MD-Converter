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

# FIX!!! hevc can be both image or video??
apple_image_codecs = ['heif', 'heic']
imagemagick_command = [
    'magick',
    'source file (automatically generated)',
    'output file (automatically generated)'
]
identify_command = [
    'identify',
    '-format',
    '\'%m\'',
    'file path (automatically generated)'
]

apple_video_codecs = ['aac', 'prores', 'aic', 'avc-intra']
ffmpeg_command = [
    'ffmpeg',
    '-i',
    'source file (automatically generated)',
    'destination (automatically generated)'
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
    'file path (automatically generated)'
]

# -----Begin Program-----
import subprocess
import os
import shutil

def main():
    # create copy of directory: 'start_directory-converted-to-md'
    copy_directory = os.path.join(os.path.dirname(start_directory), os.path.basename(start_directory) + '-converted-to-md')
    if os.path.exists(copy_directory):
        print('Please move or delete the converted files and restart')
        quit()
    else:
        os.chdir(start_directory)
        shutil.copytree(start_directory, copy_directory)
        recursiveSearch(copy_directory)
    print('Done!')

def recursiveSearch(directory):
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
                    doRtfConversion(rtfd_file_path)
                    fixMdAttachments(md_path)

            # now that the .rtf file is converted, convert images and videos
            if do_image_convert or do_video_convert:
                for rtfd_file in os.listdir(file_path):
                    rtfd_file_path = os.path.join(file_path, rtfd_file)
                    md_path = os.path.join(os.path.dirname(rtfd_file), 'TXT.md')

                    if imageCodecIsApple(rtfd_file_path) and do_image_convert:
                        print('CONVERTING IMAGE: ', rtfd_file)
                        doImageConversion(rtfd_file_path, rtfd_file)
                        fixImageAttachments(md_path, rtfd_file)
                        break;

                    if videoCodecIsApple(rtfd_file_path) and do_video_convert:
                        print("CONVERTING VIDEO: ", rtfd_file)
                        doVideoConversion(rtfd_file_path, rtfd_file)
                        fixVideoAttachments(md_path, rtfd_file)

            # rename .rtfd directory to remove '.rtfd'
            os.rename(file_path, file_path.replace('.rtfd', ''))

        elif os.path.isdir(file_path):
            recursiveSearch(file_path)

def doRtfConversion(rtf_path):
    os.chdir(os.path.dirname(rtf_path))
    # set source file in command
    pandoc_command[1] = rtf_path
    # set output file in command
    pandoc_command[7] = os.path.join(os.path.dirname(rtf_path), os.path.basename(rtf_path).split('.')[0] + '.md')
    # perform conversion to markdown using pandoc
    output = subprocess.run(pandoc_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if output.returncode != 0:
        print('ERROR pandoc: ', output.stderr.decode())
        quit()
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
    output = subprocess.run(imagemagick_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if output.returncode != 0:
        print('ERROR imagemagick: ', output.stderr.decode())
        quit()
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
    output = subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if output.returncode != 0:
        print('ERROR ffmpeg: ', output.stderr.decode())
        quit()
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

def videoCodecIsApple(video_path):
    ffprobe_command[9] = video_path
    output = subprocess.run(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if output.returncode != 0:
        print('ERROR ffprobe: ', output.stderr.decode())
        quit()
    for apple_video_codec in apple_video_codecs:
        if apple_video_codec in output.stdout.decode().strip().lower():
            return True
    return False

def imageCodecIsApple(image_path):
    identify_command[3] = image_path
    output = subprocess.run(identify_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if output.returncode != 0:
        print("ERROR identify: ", output.stderr.decode())
        quit()
    for apple_image_codec in apple_image_codecs:
        if apple_image_codec in output.stdout.decode().strip().lower():
            return True
    return False

if __name__ == '__main__':
    main()
