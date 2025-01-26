import argparse
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

#Constants
cropped_image_directory = "./cropped"
segment_map_directory = "./segmentmaps"

def main():
    #Arg parsing from input.
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--verbose", "-v", required=False, default=False, action="store_true")
    arg_parser.add_argument('--manifest', '-m', required=True, help='.txt manifest file for input data sets')

    args = arg_parser.parse_args()
    manifest_file = args.manifest
    verbose = args.verbose

    #Manifest file provides the codenames of all the image sets we want to use (ex: ts1, ts2)
    if(manifest_file == None):
        print("No manifest file provided")
        exit(1)
    print("Using" + manifest_file + " as manifest file for input data.")

    image_sets = []
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



if __name__ == "__main__":
    main()