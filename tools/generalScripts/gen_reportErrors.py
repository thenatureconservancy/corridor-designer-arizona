import sys, os, traceback, string

def addErrorMessages(gp):
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    
    pymsg = ("- PYTHON ERRORS: ---------------\n"+
             "Traceback Info:\n" + tbinfo +
             "\nError Info:\n" + str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n")
    
    # generate a message string for any geoprocessing tool errors
    msgs =  ("- GP ERRORS: -------------------\n" +
            gp.GetMessages(2) + "\n")

    # return gp messages for use with a script tool
    gp.AddMessage(pymsg)    
    gp.AddMessage(msgs)
    print(pymsg)    
    print(msgs)


