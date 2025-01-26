import argparse
import os
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import string

#Constants
cropped_image_directory = "./cropped"
segment_map_directory = "./segmentmaps"

def main():
    #Arg parsing from input.
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument("--verbose", "-v", required=False, default=False, action="store_true")
    arg_parser.add_argument('--manifest', '-m', required=False, help='.txt manifest file for input data sets')
    arg_parser.epilog = ("Manifest file requirements:\n"
                         "lines beginning with number sign # are ignored for easier temporary edits and comments\n"
                         "all images in a set must use same file extension :)\n"
                         "entries are separated by line and formatted as \"NAME, .extension, number of digits in file number\" (space after comma not strictly necessary)")
    args = arg_parser.parse_args()
    manifest_file = args.manifest
    verbose = args.verbose

    #Manifest file provides the codenames of all the image sets we want to use (ex: ts1, ts2)
    image_sets = []
    if(manifest_file == None):
        print("No manifest file provided, exiting")
        arg_parser.print_help()
        exit(1)
    print("Using " + manifest_file + " as manifest file for input data.")

    file = open(manifest_file, 'r')
    for line in file:
        line = line.strip()
        if(len(line) == 0): continue #ignore empty lines
        if(line[0] != '#'): #ignore comments
            if(verbose): print("Adding " + line + " to input sequence.")
            imset_entry = line.split(',')
            imset_entry[1] = imset_entry[1].strip()
            image_sets.append(imset_entry)
    file.close()

    if(verbose):
        print("Final input sequence")
        for item in image_sets:
            print(item)

    for entry in image_sets:
        setname = entry[0]
        extension = entry[1]
        n_digits = int(entry[2])
        i = 0
        while True:
            filenum = str(i)
            nextimage = cropped_image_directory + "/" + setname + "/" + setname + "-" + filenum.zfill(n_digits) + extension #script specific local pathing
            nextpath = os.path.normpath(nextimage) #storing os specific changes (might be abspath)
            if verbose: print("Opening:" + nextimage + ".", end="\t")
            if os.path.isfile(nextpath):
                if verbose: print("Success")
                i = i + 1
            else:
                if verbose: print("Failed")
                print("No more images found in set " + setname + ".")
                if verbose: print("HELP: Check number of extension and number of digits in manifest entry if this is incorrect.")
                break


if __name__ == "__main__":
    main()