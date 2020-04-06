import c3pm
import sys
import colorama
from termcolor import colored
import os
import tkinter as tk
from tkinter import filedialog


def openFileExplorer():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    return file_path

def main():



    #c3pm.importPack("C:\\Users\\renan\\Desktop\\c3pmTest\\source_project.c3p", "C:\\Users\\renan\\Desktop\\c3pmTest\\target_project.c3p")
    clear = lambda: os.system('cls')
    padValue = 60
    version = "0.2"

    title = ' Construct 3 Pack Manager by Relixes'
    
    print("".center(padValue, '-'))
    print(title.center(padValue, '-'))
    print("".center(padValue, '-'))
    print("Version: " + version)
    print("contact: renanfelixrodrigues@gmail.com")
    print("Info: Construct 3 Pack manager (C3PM) is a tool to share content between construct 3 projects through c3 packs.")

    input("\n\n-> Press 'Enter' to get started...")
    clear()

    print("".center(padValue, '-'))
    print(" Select the Construct 3 project ".center(padValue, '-'))
    print("".center(padValue, '-'))
    input('\n\n-> Select the c3p file that will import the c3Pack (press enter to open file explorer)...')
    clear()
    targetProjectPath = openFileExplorer()
    
    print("".center(padValue, '-'))
    print(" Select the C3 Pack ".center(padValue, '-'))
    print("".center(padValue, '-'))
    input('\n\n-> Now select the the c3pack file (press enter to open file explorer)...')
    clear()
    sourceProjectPath = openFileExplorer()


    print("Construct 3 project: " + targetProjectPath)
    print("C3 Pack: " + sourceProjectPath)
 
    print('\nImporting pack...\n')
    result = c3pm.importPack(sourceProjectPath, targetProjectPath, True)
    
    if(result['status'] == 'sucess'):
        print("* Sucess! The pack was imported! A new c3p file with the pack content was created in the target project folder!")
    else:
        print("* Oops... We had a problem. Error: ")
        print(result['error'])
        
    input("-> Press any key to close the program...")

if __name__== "__main__":
    main()