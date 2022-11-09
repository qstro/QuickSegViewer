#Copyright (c) 2022, Quirin Strotzer
#All rights reserved.

#This source code is licensed under the AGPL-3.0 license license found in the
#LICENSE file in the root directory of this source tree. 


import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.widgets import Slider, TextBox
import SimpleITK as sitk
import numpy as np
import os
from pathlib import Path

# Folder containing subfolders 'img' (image data) and 'mask' (segmentation masks)
path = 'data'

# text file in the 'data' subfolder with case ids, one per line
patients = sorted([line.rstrip('\n') for line in open(os.path.join(path, 'patients.txt'))])

def multi_slice_viewer(volume1, volume2, volume3, volume4, mask):
    '''
    main function to plot the image and mask data.

    imput:
    - image volumes and mask as np.array
    '''

    # used to count and switch between cases
    global number

    # remove interfering default key bindings of matplotlib
    remove_keymap_conflicts({   'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
                                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 
                                'up', 'down', 'escape', 'left', 'right'})

    # in our case a row with four subplots is created; can be altered as needed
    fig, ax = plt.subplots(1, 4, gridspec_kw = {'bottom': 0, 'top': 1, 'left':0,
                                                'right': 1, 'wspace':0, 'hspace':0})

    fig.suptitle((f'{patients[number]}\nNumber {number+1} of {len(patients)}\n'
                'arrows = up/down and next/previous patient, esc = close window\n'
                'blue = edema, yellow = necrosis, red = enhancing tumor'), 
                fontsize=16, color ='white')

    fig.tight_layout()
    fig.set_facecolor('black')

    # default value for opacity slider
    OPACITY = 0.3
    
    # add slider for opacity
    axfreq = fig.add_axes([0.15, 0.1, 0.7, 0.03])
    fig.slider0 = Slider(ax=axfreq, label='opacity', valmin=0, valmax=1, valinit=OPACITY)
    fig.slider0.label.set_color('white')

    # add text box to switch between cases
    axtext = fig.add_axes([0.15, 0.15, 0.7, 0.03])
    fig.text_box = TextBox(ax=axtext, label='Choose Case', initial=number+1)
    fig.text_box.on_submit(submit)
    fig.text_box.label.set_color('white')

    # add text box for commenting each case
    axtext2 = fig.add_axes([0.15, 0.05, 0.7, 0.03])
    fig.text_box2 = TextBox(ax=axtext2, label='Segmentation Comment', initial='')
    fig.text_box2.on_submit(segfail)
    fig.text_box2.label.set_color('white')

    axtext3 = fig.add_axes([0.15, 0.01, 0.7, 0.03])
    axtext3.text(0, 1,  ('Insert comment for current segmentation above and press enter. ' 
                        'Information will be stored in data/failed_segmentations.txt'),
                        transform=axtext3.transAxes, fontsize=14,
                        verticalalignment='top', backgroundcolor = 'black',
                        color='white')
    axtext3.set_facecolor('black')

    mask0 = [None, None, None, None]

    volumes = [volume1, volume2, volume3, volume4]

    # plot images and overlay mask
    for i in range(4):

        ax[i].volume = volumes[i]
        ax[i].mask = mask
        ax[i].index = volumes[i].shape[0] // 2

        ax[i].imshow(volumes[i][ax[i].index], cmap='gray', interpolation='none')
        mask0[i] = ax[i].imshow(mask[ax[i].index], cmap='jet', alpha=OPACITY, interpolation='none', norm = Normalize(vmin=0, vmax=3))

    fig.slider0.on_changed(lambda value: [x.set_alpha(value) for x in mask0])

    fig.canvas.mpl_connect('key_press_event', process_key)
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    for axs in ax.flat:
        axs.axis('off')

    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    plt.show(block=True)

def submit(text):
    '''
    switch to case specified by inserted number

    input:
    - text from text box
    '''
    global number
    number = int(text)-1

    fig = plt.gcf()

    # load case
    next_pat(number)
    plt.close(fig)

def segfail(text):
    '''
    stores comment and case id in data/failed_segmentations.txt as a new line

    input:
    - text from text box
    '''

    global number
    
    fig = plt.gcf()

    if text != 'saved':
        with open(os.path.join(path, 'failed_segmentations.txt'), 'a+') as file:
            file.write(f'{patients[number]}: {text}')
            file.write('\n')

    fig.text_box2.set_val("saved")

def process_key(event):
    '''
    custom key bindings

    input:
    - key event
    '''
    global number

    fig = event.canvas.figure

    ax = fig.axes

    print(event.key)

    if event.key == 'up':
        previous_slice(ax)

    elif event.key == 'down':
        next_slice(ax)

    elif event.key == 'right':
        number += 1
        print('next patient')
        next_pat(number)
        plt.close(fig)

    elif event.key == 'left':
        number -= 1
        print('previous patient')
        next_pat(number)
        plt.close(fig)

    elif event.key == 'escape':
        
        plt.close('all')
        print('close')

    fig.canvas.draw_idle()

def on_scroll(event):
    '''
    enables mouse wheel scrolling

    input:
    - scroll event
    '''
    fig = event.canvas.figure

    ax = fig.axes

    if event.button == 'up':
        previous_slice(ax)
    elif event.button == 'down':
        next_slice(ax)

    fig.canvas.draw_idle()

def previous_slice(ax):
    '''
    shows previous slice in z-direction

    input:
    - figure axes
    '''

    for axs in ax[:4]:
        volume = axs.volume
        mask = axs.mask
        axs.index = (axs.index - 1) % volume.shape[0]

        axs.images[0].set_array(volume[axs.index])
        axs.images[1].set_array(mask[axs.index])
    

def next_slice(ax):
    '''
    shows next slice in z-direction

    input:
    - figure axes
    '''

    for axs in ax[:4]:
        volume = axs.volume
        mask = axs.mask
        axs.index = (axs.index + 1) % volume.shape[0]

        axs.images[0].set_array(volume[axs.index])
        axs.images[1].set_array(mask[axs.index])
    

def remove_keymap_conflicts(new_keys_set):
    '''
    removes conflicts of matplotlib default key bindings

    input:
    - keys that should be removed
    '''
    for prop in plt.rcParams:
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)

def next_pat(num):
    '''
    loads image and mask files of case at the specified location in patients list

    input:
    - position of case in patients list as int
    '''
    global number
    number = num
    
    # files had to be rotated by 180 degrees in our case
    volume1_array = np.rot90(sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(path, 'img', f'{patients[number]}_0000.nii.gz'))), 2)
    volume2_array = np.rot90(sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(path, 'img', f'{patients[number]}_0001.nii.gz'))), 2)
    volume3_array = np.rot90(sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(path, 'img', f'{patients[number]}_0002.nii.gz'))), 2)
    volume4_array = np.rot90(sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(path, 'img', f'{patients[number]}_0003.nii.gz'))), 2)
    mask_array = np.rot90(sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(path, 'mask', f'{patients[number]}.nii.gz'))), 2)
    mask_array = np.ma.masked_where(mask_array==0, mask_array)
    multi_slice_viewer(volume1_array, volume2_array, volume3_array, volume4_array, mask_array)

# start with case at position 0
next_pat(0)