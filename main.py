import c3pm
import sys

def main():

    #c3pm.importPack("C:\\Users\\renan\\Desktop\\c3pmTest\\source_project.c3p", "C:\\Users\\renan\\Desktop\\c3pmTest\\target_project.c3p")
   
    if len(sys.argv) > 1:
        if sys.argv[1] == 'import':
            c3pm.importPack(sys.argv[2], sys.argv[3])
        else:
            print('false')
    else:
        print('false')

if __name__== "__main__":
    main()