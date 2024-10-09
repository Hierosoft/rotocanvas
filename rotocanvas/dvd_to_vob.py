#!/usr/bin/env python

from __future__ import print_function
import os
import subprocess
import sys
import getpass
import argparse

def install_package(package_name):
    """Install a package using apt-get."""
    try:
        subprocess.run(['sudo', 'apt-get', 'install', '-y', package_name], check=True)
    except subprocess.CalledProcessError:
        print("Failed to install %s." % package_name)
        sys.exit(1)

def find_longest_title(dvd_path):
    """Find the longest title on the DVD."""
    try:
        output = subprocess.check_output(['lsdvd', dvd_path], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("Error reading the DVD information using lsdvd.")
        sys.exit(1)

    # Parse the output of lsdvd to find the longest title
    longest_title = None
    max_length = 0

    for line in output.splitlines():
        if 'Length:' in line:
            parts = line.split(',')
            title_info = parts[0].strip()
            counts_info = [info.strip() for info in parts[1].split("Chapters:", 1)]
            length_info = counts_info[0].replace('Length:', '').strip()
            chapter_count = None
            if len(counts_info) > 1:
                chapter_count = int(counts_info[1].strip())

            # Parse length to seconds
            hours, minutes, seconds = map(float, length_info.split(':'))
            length_in_seconds = hours * 3600 + minutes * 60 + seconds

            # Update longest title if this one is longer
            if length_in_seconds > max_length:
                max_length = length_in_seconds
                longest_title = title_info.split(': ')[1]

    return longest_title

def copy_longest_title(dvd_path, longest_title, output_dir):
    """Copy and decrypt the longest title using mplayer."""
    output_file = os.path.join(output_dir, 'longest_title_movie.vob')
    print("Copying and decrypting title %s to %s..." % (longest_title, output_file))

    command = [
        'mplayer',
        'dvd://%s' % longest_title,
        '-dvd-device', dvd_path,
        '-dumpstream', '-dumpfile', output_file
    ]
    try:
        subprocess.run(command, check=True)
        print("Successfully saved the longest title to %s" % output_file)
    except subprocess.CalledProcessError:
        print("Failed to copy the longest title.")
        sys.exit(1)

def find_dvd_path(dvd_path=None):
    """Automatically search for a DVD in /media/<username> if no DVD path is provided."""
    if dvd_path:
        return dvd_path

    username = getpass.getuser()
    media_path = '/media/%s' % username
    potential_dvds = []

    # Search for folders containing VIDEO_TS
    for subfolder in os.listdir(media_path):
        subfolder_path = os.path.join(media_path, subfolder)
        video_ts_path = os.path.join(subfolder_path, 'VIDEO_TS')
        if os.path.isdir(video_ts_path):
            potential_dvds.append(subfolder_path)

    # Handle the case of no DVDs or multiple DVDs
    if len(potential_dvds) == 0:
        print("No DVD found in /media/%s." % username)
        sys.exit(1)
    elif len(potential_dvds) > 1:
        print("More than one DVD found. Please specify which one to use.")
        for dvd in potential_dvds:
            print(" - %s" % dvd)
        sys.exit(1)

    # Return the path of the single DVD found
    return potential_dvds[0]

def main():
    parser = argparse.ArgumentParser(description='Copy the longest title from a DVD.')
    parser.add_argument('-i', '--dvd_path', type=str, help='Path to the DVD.')
    parser.add_argument('-o', '--output_path', type=str, help='Path to save the output VOB file.')

    args = parser.parse_args()

    # Find the DVD path
    dvd_path = find_dvd_path(args.dvd_path)

    output_dir = os.path.expanduser("~/tmp")

    # Set output sub-path based on DVD path or user-defined output path
    if args.output_path:
        sub_path = args.output_path
    else:
        dvd_name = os.path.split(dvd_path)[1]
        sub_path = os.path.join(output_dir, dvd_name)

    # Create output directory if it doesn't exist
    if not os.path.exists(sub_path):
        os.makedirs(sub_path)

    # Check if lsdvd is installed
    if subprocess.call(['which', 'lsdvd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        print("lsdvd is not installed. Installing it...")
        install_package('lsdvd')

    # Check if mplayer is installed
    if subprocess.call(['which', 'mplayer'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        print("mplayer is not installed. Installing it...")
        install_package('mplayer')

    # Find the longest title on the DVD
    longest_title = find_longest_title(dvd_path)
    if longest_title is None:
        print("Failed to determine the longest title.")
        sys.exit(1)

    print("The longest title is: %s" % longest_title)

    # Copy and decrypt the longest title
    copy_longest_title(dvd_path, longest_title, sub_path)

if __name__ == '__main__':
    main()
