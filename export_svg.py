import os
import string

def export_svg():
    for file in os.listdir("svg"):
        if os.name == 'nt':
            command = '"c:\Program Files\Inkscape\Inkscape.exe"'
        else:
            command = "inkscape"
        for i in [2**a for a in range(3,8)]:
            print "Exporting "+file+" at size "+str(i)
            invocation = command+" -f svg/"+file+" -e asset/"+file.replace('.svg','_'+str(i)+'.png')+" --export-width="+str(i)+" --export-height="+str(i)
            print invocation
            os.system(invocation)
    
    
if __name__ == '__main__':
    export_svg()
    print os.getcwd()