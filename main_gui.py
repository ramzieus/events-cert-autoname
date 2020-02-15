#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# events-cert-autoname
# 
# Version: v0.1.3
# Date: 2020-02-14

# Copyright (c) 2020 Abderraouf Adjal <abderraouf.adjal@gmail.com>
# 
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Tool to write names on a list to an image.
# This is used to save time when generate attendance certificates for events.
#
# For usage help:
#   % python3 main.py --help
#
# Usage examples:
#   % python3 main.py "list.csv" "cert.png" "et-book-bold-line-figures.ttf" "certs_output/"
#   % python3 main.py "list.csv" "cert.png" "et-book-bold-line-figures.ttf" "certs_output/" -s 42 -k "#000000" -y 200
#   % python3 main.py "list.csv" "cert.png" "et-book-bold-line-figures.ttf" "certs_output/" --fontsize 42 -k "#000000" -y 200 --replace
#
# Install requirements:
#   % pip3 install --user -r requirements.txt
#
# NOTE: - For Arabic names, try to use the font <DejaVuSans.ttf>
#       - For the CSV file, Use comma to separate values (NAME, EMAIL).
#       - This script tested for GNU/Linux OS.

import os
import argparse
from sys import stderr as sys_stderr
from csv import reader as csv_reader
from arabic_reshaper import reshape as arabic_reshaper_reshape
from PIL import Image, ImageFont, ImageDraw
from bidi.algorithm import get_display as bidi_algorithm_get_display
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar


# def get_input_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('csv_list', type=str,
#                         help = 'Path to names list CSV file (NAME, EMAIL).')
#     parser.add_argument('cert_img', type=str,
#                         help = 'Path to certificate image file.')
#     parser.add_argument('font_file', type=str,
#                         help = 'Font file (truetype).')
#     parser.add_argument('output_dir', type=str,
#                         help = 'Path to the export folder.')
#     parser.add_argument('-s', '--fontsize', type=int, default=48, 
#                         help = 'Font size.')
#     parser.add_argument('-k', '--colorhex', type=str, default='000000', 
#                         help = 'RGB font color in HEX.')
#     parser.add_argument('-x', type=int, default=None,
#                         help = 'Text position X, In center by default.')
#     parser.add_argument('-y', type=int, default=None,
#                         help = 'Text position Y, In center by default.')
#     parser.add_argument('-r', '--replace', action='store_true',
#                         help = 'Force replace/overwrite the list outputs.')
#     return parser.parse_args()


def csv_to_dict(ppl, namesfile):
    with open(namesfile, 'r') as fd:
        read_csv = csv_reader(fd, delimiter=',')
        for row in read_csv:
            row[0] = row[0].strip().title() # The person name
            row[1] = row[1].strip() # The e-mail
            ppl.append(tuple((row[0], row[1])))


def make_person_cert(name, email, cert_img, out_cert, fontfile, fontsize, color_tuple, x, y):
    img = Image.open(cert_img).convert('RGB')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font=fontfile, size=fontsize)
    name_reshaped = arabic_reshaper_reshape(name) # Correct shape
    name_reshaped_directed = bidi_algorithm_get_display(name_reshaped) # Correct direction
    # Text in center as default option
    if (x is None):
        x = int((img.size[0] - font.getsize(name_reshaped_directed)[0]) / 2)
    if (y is None):
        y = int((img.size[1] - font.getsize(name_reshaped_directed)[1]) / 2)
    draw.text((x, y), name_reshaped_directed, fill=color_tuple, font=font, align='center') # ((x, y),"Text",(r,g,b))
    img.save(out_cert, format='PDF')
    return True

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.filename = ""
        self.output = ""
        self.cert = ""
        self.font = ""
        self.fontsize = 48
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        
        #csv button
        self.csv = tk.Button(self, width=40, height=2)
        self.csv["text"] = "Select csv file"
        self.csv["command"] = self.get_file_name
        self.csv.pack(side="top")


        #output button
        self.out = tk.Button(self, width=40, height=2)
        self.out["text"] = "Select folder output"
        self.out["command"] = self.set_output
        self.out.pack()


        #Font button
        self.font_btn = tk.Button(self, width=40, height=2)
        self.font_btn["text"] = "Select Font Family"
        self.font_btn["command"] = self.get_font
        self.font_btn.pack()

        #Cert button
        self.cert_btn = tk.Button(self, width=40, height=2)
        self.cert_btn["text"] = "Select Certificate form"
        self.cert_btn["command"] = self.get_cert
        self.cert_btn.pack()
        
        #Generate button
        self.gen = tk.Button(self, width=40, height=2)
        self.gen["text"] = "Generate Certs"
        self.gen["command"] = self.gen_cert
        self.gen.pack()
        
        #Progress bar
        self.progress = Progressbar(root, orient = tk.HORIZONTAL, length = 200, mode = 'determinate')
        self.progress.pack()

    def get_file_name(self):
        self.filename =  filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        self.csv.configure(bg = "green")
        self.csv.configure(fg = "white")
        root.update_idletasks()
    
    def set_output(self):
        self.output = filedialog.askdirectory(initialdir = ".",title = "Select Directory")
        self.out.configure(bg = "green")
        self.out.configure(fg = "white")

    def get_font(self):
        self.font =  filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("TTF files","*.ttf"),("OTF files","*.otf"),("all files","*.*")))
        self.font_btn.configure(bg = "green")
        self.font_btn.configure(fg = "white")

    def get_cert(self):
        self.cert = filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("PNG files","*.png"),("all files","*.*")))
        self.cert_btn.configure(bg = "green")
        self.cert_btn.configure(fg = "white")

    def gen_cert(self):

        if (os.path.exists(self.output) == False):
            try:
                os.makedirs(self.output)
            except:
                print('  ** ERROR: Can NOT make the output folder. Exit.', file=sys_stderr)
                exit(1)
            
        if (os.path.isdir(self.output) == False):
            print('  ** ERROR: "{0}" is not a folder. Exit.'.format(self.output), file=sys_stderr)
            exit(1)

        colorhex = "000000".lstrip('#')
        color_tuple = tuple(int(colorhex[i:i+2], 16) for i in (0, 2, 4))
        ppl = list() # [('name', 'email'), ('name', 'email')]
        csv_to_dict(ppl, self.filename)
        count = 0
        print('Processing...')
        f = open(self.filename)
        num = len(f.readlines())
        for person in ppl:
            try:
                out_cert = os.path.join(self.output, '{0}+{1}+{2}.pdf'.format(os.path.splitext(self.cert)[0].split('/')[-1], person[0], person[1]))
                if ((False == False) and (os.path.exists(out_cert) == True)):
                    print('\n  ** WARNING: The path for output "{0}" exists.'.format(out_cert), file=sys_stderr)
                    q = str(input('  >> Replace the file? [Y or N] (N): ')).strip().lower()
                    if (q != 'y'):
                        continue
                # make_person_cert(name, email, cert_img, out_cert, fontfile, fontsize, color_tuple, x, y)
                r = make_person_cert(person[0], person[1], self.cert, out_cert, self.font,self.fontsize, color_tuple, None,None)
                if (r == True):
                    print('{0}  -  {1}'.format(person[0], person[1]))
                    count += 1
                    self.progress['value'] = self.progress['value'] + (count * 100 / num)
                    root.update_idletasks()
            except:
                print('  ** ERROR: With [{0}, {1}]. Exit.'.format(person[0], person[1]), file=sys_stderr)
                exit(1)
            
        print('\nTotal of "{0}" files made in "{1}".'.format(count, self.output))
        

root = tk.Tk()
root.title("Events Cert Autoname")
root.iconbitmap(r'C:\Users\ramzi\Desktop\events-cert-autoname\Assets\icon.ico')
app = Application(master=root)
app.mainloop()