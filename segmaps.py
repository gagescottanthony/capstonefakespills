import argparse
import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import string

from matplotlib.pyplot import imshow
from numpy.ma.core import zeros_like

#Constants
cropped_image_directory = "./cropped"
segment_map_directory = "./segmentmaps"
opacity_map_directory = "./opacitymaps"
global verbose
global willsave
global showplots

def main():
    global verbose, willsave, showplots
    #Arg parsing from input.
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument("--verbose", "-v", required=False, default=False, action="store_true")
    arg_parser.add_argument('--manifest', '-m', required=False, help='.txt manifest file for input data sets')
    arg_parser.add_argument('--save', '-s', required=False, default=False, action="store_true", help='flag to save files')
    arg_parser.add_argument('--showplots', '-p', required=False, default=False, action="store_true",
                            help='flag to show matplotlib plots')
    arg_parser.epilog = ("Manifest file requirements:\n"
                         "lines beginning with number sign # are ignored for easier temporary edits and comments\n"
                         "all images in a set must use same file extension :)\n"
                         "entries are separated by line and formatted as \"NAME, .extension, number of digits in file number\" (space after comma not strictly necessary)")
    args = arg_parser.parse_args()
    manifest_file = args.manifest

    verbose = args.verbose
    if(verbose): print("Using verbose mode!")

    willsave = args.save
    if(willsave): print("Will save files when done!")

    showplots = args.showplots
    if(showplots): print("Using showplots mode!")

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
        i = 0
        while True:
            nextimage = list(entry_to_filename(i, entry)) # has strings for \setname\setname-number.extension and setname-number.extension
            nextpath = os.path.normpath(cropped_image_directory + nextimage[0]) #storing os specific changes (might be abspath)
            if verbose: print("Opening:" + nextimage[0] + ".", end="\t")
            if os.path.isfile(nextpath):
                if verbose: print("Success")
                create_segmap(entry, nextpath, nextimage)
                i = i + 1
            else:
                if verbose: print("Failed")
                print("No more images found in set " + entry[0] + ".")
                if verbose: print("HELP: Check number of extension and number of digits in manifest entry if this is incorrect.")
                break

def entry_to_filename(i, entry):
    "takes entry list (setname, extension, n_digits) and returns script specific local pathing (working directory). second return value is small filename only (not path)"
    setname = entry[0]
    extension = entry[1]
    n_digits = int(entry[2])
    filenum = str(i)
    return "/" + setname + "/" + setname + "-" + filenum.zfill(n_digits) + extension, setname + "-" + filenum.zfill(n_digits)

def create_segmap(entry, nextpath, filename):
    global verbose, willsave, showplots

    #confirm image is readable
    untreated_image = cv2.imread(nextpath)
    if untreated_image is None:
        print("Image did not load for path: " + nextpath + ".")
        return None
    (h, w, c) = untreated_image.shape[:3]
    if verbose: print("height: %d, width: %d, channels %d." % (h, w, c))

    gray_image = cv2.cvtColor(untreated_image, cv2.COLOR_RGB2GRAY)
    colour_val = np.full_like(gray_image, 0) #create a channel for a fully black image of proper size
    alpha_channel = cv2.bitwise_not(gray_image) #invert white(255) into 0 (fully transparent) and black(0) into fully opaque(255)
    converted_image = cv2.merge((colour_val, colour_val, colour_val, alpha_channel)) #image where every pixel is black, using alpha channel for shading


    #todo: replace this crammed in noise file with a smart algo
    noise = cv2.imread("Test_noise 1.jpg")
    crop_noise = cv2.resize(noise, (w, h))

    mask = gray_image
    cv2.threshold(gray_image, 235, 255, type=cv2.THRESH_BINARY, dst=mask)
    cv2.bitwise_not(mask, mask)
    zeros = zeros_like(mask)
    segmap = cv2.merge((mask,zeros,zeros))

    if willsave:
        #todo: destination directory needs to already exist or imwrite will silently fail. need to add a directory creation step!
        savename = segment_map_directory + filename[0]
        if verbose: print("Saving segmap to: " + savename)
        cv2.imwrite(savename, cv2.cvtColor(segmap, cv2.COLOR_RGB2BGR))

        #has to use png to preserve alpha channel
        altfilename = filename[0][:filename[0].rfind('.')] + ".png"
        savename = opacity_map_directory + altfilename
        cv2.imwrite(savename, converted_image) #BGR vs RGB doesnt matter

    if showplots:
        plt.suptitle(filename[1] + " " + str(h) + "x" + str(w) + " w/ " + str(c) + " channels")

        plt.subplot(1, 3, 1)
        plt.title("untreated")
        plt.imshow(untreated_image)

        plt.subplot(1, 3, 2)
        plt.title("conversion w/ background")
        plt.imshow(crop_noise)
        plt.imshow(converted_image)

        plt.subplot(1, 3, 3)
        plt.title("segmap in red")
        plt.imshow(segmap)


        plt.show()
    return

if __name__ == "__main__":
    main()