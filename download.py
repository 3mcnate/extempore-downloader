from concurrent.futures import ThreadPoolExecutor
import os
import requests
import math
import subprocess
from termcolor import colored
from colorama import init


"""
URL is in format: https://vz-3c1714c0-443.b-cdn.net/7f6ad385-c475-45e0-9330-705e8176881d/1080p/
                                                                                              ^ slash at the end
"""

init()
def print_error(text) : print(colored("Error: ", 'red', attrs=['bold']) + text)
def print_success(text) : print(colored(text, 'green', attrs=['bold']))
def print_yellow(text) : print(colored(text, 'yellow'))

def download_video(url, length, name):
    try:
        print_yellow(f"Downloading video {name} ({url})...")

        # makes directory relative to PWD to store fragments
        dir_name = url.split('/')[-3]
        os.mkdir(dir_name)

        # number of fragments to download concurrently
        NUM_THREADS = 100

        # start downloading fragments for this video
        num_fragments = math.ceil(length / 4)
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:

            # submit one job for each fragment
            for i in range(num_fragments):
                executor.submit(download_fragment, url, i)

        # waits until executor is done, call ffmpeg script
        success = combine_fragments(dir_name, name)

        if success: 
            print_success(f"Successfully downloaded video '{name}.mp4' ({dir_name})")
        else:
            print_error(f"Couldn't download video '{name}.mp4' ({dir_name})")

    finally:
        # cleanup
        print("Cleaning up directory...")
        cleanup_dir(dir_name)


def download_fragment(base_url, number):

    # name of directory to store fragment
    dir_name = base_url.split('/')[-3]

    # make request
    response = requests.get(base_url + f"video{number}.ts")

    # check response status
    if response.status_code != 200:
        print_error(f"Error {response.status_code}: Couldn't get fragment {number} of video {dir_name}")
    else:
        # write .ts file to the correct folder
        with open(f"{dir_name}/video{number}.ts", 'wb') as file:
            file.write(response.content)


def combine_fragments(fragments_dir, name):
    print(f"Combining fragments from video {fragments_dir} ({name})...")

    # sanitize video name which could contain spaces for shell format
    shell_name = '\\ '.join(name.split(' '))

    # from https://superuser.com/a/1267448
    command = f"for i in `\ls {fragments_dir}/*.ts | sort -V`; do echo \"file '$i'\"; done >> {fragments_dir}.txt && ffmpeg -f concat -i {fragments_dir}.txt -c copy -bsf:a aac_adtstoasc videos/{shell_name}.mp4"

    # run the subprocess with output disabled
    devnull = open('/dev/null', 'w')
    result = subprocess.run(command, shell=True, stdout=devnull)
    
    # error checking
    if result.returncode != 0:
        print_error(
            f"There was an error combining fragments from video {fragments_dir} ({name})")
        return False

    return True


def cleanup_dir(dir_name):
    # delete files in directory
    for file in os.listdir(dir_name):
        os.remove(os.path.join(dir_name, file))
    
    # delete directory
    os.rmdir(dir_name)

    # delete leftover text file
    os.remove(dir_name + '.txt')


def get_length_in_seconds(length):
    try:
        time_list = length.split(':')
        time_list = list(map(lambda x: int(x.strip()), time_list))

        if len(time_list) == 2:
            seconds = time_list[0] * 60 + time_list[1]
        elif len(time_list) == 3:
            seconds = time_list[0] * 3600 + time_list[1] * 60 + time_list[2]

        return seconds

    except Exception:
        return -1


def main():

    print("Extempore Video Downloader.")

    # make output video folder
    try:
        os.mkdir('videos')
    except FileExistsError:
        pass

    urls_path = input("What file are the urls in? (enter for urls.txt) ")
    if urls_path == "":
        urls_path = "urls.txt"

    """
    FILE FORMAT:

    https://vz-3c1714c0-443.b-cdn.net/7f6ad385-c475-45e0-9330-705e8176881d/1080p/ + 16:16 + Pre-course 1. Ida Vogel - NIPT andor combined 1st Trimester Screening.Fetal genotype vs. phenotype 
    https://vz-3c1714c0-443.b-cdn.net/a93615a3-9ff4-41e8-b5b8-9f081edc4c48/1080p/ + 26:44 + Pre-course 2. John Hyett - Fetal anomalies karyotype vs. microarray vs. exomes and whole genome sequencing
    ...
    
    """

    # read input file
    try:
        file = open(urls_path, 'r')
        lines = file.readlines()
        file.close()
    except OSError:
        print_error(f"Couldn't read/open file '{urls_path}'")

    # thread pool to download videos
    executor = ThreadPoolExecutor(3)

    # download each video line
    for line in lines:
        url, length, name = line.split(' + ')
        name = name.strip()
        length_seconds = get_length_in_seconds(length)
        if length_seconds == -1:
            print_yellow(f'Incorrectly formatted time: {length}')
            print_yellow(f'Skipping download of video {url}')
        else:
            executor.submit(download_video, url, length_seconds, name)

    executor.shutdown()


if __name__ == "__main__":
    main()
    #download_video("https://vz-3c1714c0-443.b-cdn.net/7f6ad385-c475-45e0-9330-705e8176881d/1080p/", 977, 'Pre-course 1. Ida Vogel - NIPT andor combined 1st Trimester Screening.Fetal genotype vs. phenotype')
