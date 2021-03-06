import SCH_TO_CSV_OOP_LIB
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from configparser import ConfigParser
import os


mainFile = SCH_TO_CSV_OOP_LIB.SCH_FILE()
openCSVFile = SCH_TO_CSV_OOP_LIB.CSV_FILE()
initialDirectory = "" 
FieldsConfigFile = "FieldKeywords.conf"
Fieldlist = [];


def ReadSettings():
	
	try:
		f = open(FieldsConfigFile)
		
	except IOError:
		print("Error: can\'t find file or read data")
	configfile = f.readlines()
	if "KiCAD PLE Config file v1.0" in configfile[0]:
		
		for line in range(1, len(configfile)-1):
			initPos =1
			newField = SCH_TO_CSV_OOP_LIB.KiCAD_Field()
			if configfile[line][0] == "<" and configfile[line][-2] == ">":
				endPos = configfile[line].find("|");
				
				newField.name = configfile[line][initPos:endPos]
				newField.appendAlias(newField.name)
				initPos = endPos
				endPos = configfile[line].find("|",initPos+1);
				while not endPos == -1:
				
					newField.appendAlias(configfile[line][initPos+1:endPos])
					initPos = endPos
					endPos = configfile[line].find("|",initPos+1);
					
				newField.appendAlias(configfile[line][initPos+1:-2])
				
			global Fieldlist
			Fieldlist.append(newField)
			
		
	else:
		print("incorrect config file")

def OpenFile():
	config = ConfigParser()
	config.read('config.ini')
    
	initialDirectory = config.get('main', 'lastDirectory', fallback="")
	if initialDirectory == "": 
		root.filename = filedialog.askopenfilename(filetypes = (("KiCAD Schematic Files",".sch"),("All Files", ".*")))
	else:
		root.filename = filedialog.askopenfilename(initialdir = initialDirectory, filetypes = (("KiCAD Schematic Files",".sch"),("All Files", ".*")))
	filename = root.filename
	root.SCHFILELAST = filename


	config.read('config.ini')
	if config.has_section('main') == FALSE:
		config.add_section('main')
	config.set('main', 'lastDirectory', os.path.dirname(filename))

	with open('config.ini', 'w') as f:
		config.write(f)

	
	if filename[-4:] == ".sch" or filename[-4:] == ".SCH":
		try:
			f = open(filename)
		except IOError:
			print("Error: can\'t find file or read data")
		else:
			mainFile.setPath(filename)
			data_test_dump = f.readlines()[0]
			f.close()

		if data_test_dump[:-1] == "EESchema Schematic File Version 2":
			#verify it conforms to KiCAD specs
			if mainFile.getComponents():
				mainFile.deleteContents()
			try:
				f = open(filename)
			except IOError:
				print("Error: can\'t find file or read data")
			else:
				mainFile.SetContents(f.readlines())
				mainFile.fieldList = Fieldlist;
				#print(FieldList)

				for i  in range(len(filename)): # get the last part of the file path

					if "/" in filename[len(filename)-1-i]:
						mainFile.setSchematicName(filename[len(filename)-i:])
						break
					#if "\" in filename[len(filename)-1-i]: UNIX PATH SUPPORT ??
					#	mainFile.setSchematicName(filename[len(filename)-i:])
					#	print(mainFile.getSchematicName())
					#	break
				f.close()
				if mainFile.ParseComponents():
					if(len(mainFile.getSubCircuits()) != len(mainFile.getSubCircuitName())):
						messagebox.showerror("FileParseError", "Hierarchical schematics could not be found")
					else:
						messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document.")

		else:
			messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document.")

	else:
		if filename:
			messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document.")

	for i in range (len(mainFile.getComponents())):
		if "?" in mainFile.getComponents()[i].GetAnnotation():
			if messagebox.askyesno("Annotation Incomplete", "The program is unable to process unanotated components. Do you want to clear imported data?"):
				mainFile.deleteContents()
			break
		#mainFile.getComponents()[i].generateProperties()
	root.initialDirectory = setInitialDirectory(filename)

	if mainFile.getSchematicName():
		statusLabel['text'] = "Loaded schematic: " + mainFile.getSchematicName() + "\n" + str(mainFile.numb_of_comps) + " components were found"
	else:
		statusLabel['text'] = "Start by loading a KiCad schematic file..."

	
	
def setInitialDirectory(filename):
	for i  in range(len(filename)): # get the last part of the file path
				if "/" in filename[len(filename)-1-i]:
					mainFile.setSchematicName(filename[len(filename)-i:])
					return filename[:len(filename)-i-1]
					break
def GenerateCSV():
	initialDirectory = root.initialDirectory
	if mainFile.get_number_of_components() > 0:
		root.path_to_save = filedialog.asksaveasfilename(initialdir = initialDirectory, filetypes = (("Comma seperated values", ".csv"),("All Files",".*")))
		root.initialDirectory = initialDirectory = setInitialDirectory(root.path_to_save)
		sortParts()
		if mainFile.SaveBOMInCSV(root.path_to_save):
			messagebox.showerror("File IOerror", "The file might still be opened")
		else:
			statusLabel['text'] = "Saved: " + str(root.path_to_save)
	else:
		messagebox.showerror("Cannot generate .CSV", "No SCH File loaded")
def Break():
	root.quit()

def listParts():
	#print("test") this somehow get executed
	#print("hoi")
	if mainFile.get_number_of_components() != 0:
		sub  = Tk()
		height = mainFile.get_number_of_components()

		for i in range(height): #Rows
				b = Entry(sub, text="")
				b.grid(row=i, column=1)
				b.insert(0,mainFile.getComponents()[i].GetAnnotation())

				c = Entry(sub, text="")
				c.grid(row=i, column=2)
				c.insert(0,mainFile.getComponents()[i].GetName())

				d = Entry(sub, text="")
				d.grid(row=i, column=3)
				#d.insert(0,mainFile.getComponents()[i].GetFarnellLink())
				d.insert(0,"deprecated")

def checklower(lowest_known, to_compare):
	#returns 1 if lower
	for i in range(len(lowest_known)):
		if i  == len(to_compare):
			return 1 #to compare is shorter i.e. lower

		if lowest_known[i] < to_compare[i]:
			if lowest_known[i].isdigit() and to_compare[i].isdigit():
				if len(to_compare) < len(lowest_known):
					return 1 #if to_compare is shorter but a digit in the string is higher than it is still lower
			return 0
		if lowest_known[i] > to_compare[i]:
			
			if lowest_known[i].isdigit() and to_compare[i].isdigit():
				if len(lowest_known) == len(to_compare):
					return 1
				if len(lowest_known) < len(to_compare):
					return 0 #if lowest_known is shorter but digit is higher then lowest known is still lower
			else:
				return 1
	return 0

def sortList(this_list):
	sortedList = []
	lowest_known = "zzzzzzz"
	position = 0

	for i in range(len(this_list)):

		for p in range(i,len(this_list)):

			if checklower(lowest_known,this_list[p]):
				lowest_known = this_list[p]
				position = p

		this_list[i] , this_list[position] = this_list[position] , this_list[i]
		lowest_known = "zzzzzzz"

	sortList = this_list

	return sortedList

def sortParts():
	mainFile.get_number_of_components()
	componentNameList = []
	for i in range (mainFile.get_number_of_components()):
		componentNameList.append(mainFile.getComponents()[i].GetAnnotation())
	sortList(componentNameList)
	for i in range (mainFile.get_number_of_components()):
		for p in range(i, mainFile.get_number_of_components()):
			if componentNameList[i] == mainFile.getComponents()[p].GetAnnotation():
				mainFile.SwapComponents(i,p)

def loadCSV():
	initialDirectory = root.initialDirectory
	mainFile.printprops()
	if initialDirectory == "": 
		root.filename = filedialog.askopenfilename(filetypes = (("KiCAD Partslist-editor files",".csv"),("All Files", ".*")))
	else:
		root.filename = filedialog.askopenfilename(initialdir = initialDirectory, filetypes = (("KiCAD Partslist-editor files",".csv"),("All Files", ".*")))
	
	filename = root.filename
	
	#root.initialDirectory = setInitialDirectory(filename) this breaks changes mainFile.schematicname
	
	if filename[-4:] == ".csv" or filename[-4:] == ".CSV":
		try:
			f = open(filename)
		except IOError:
			messagebox.showerror("File IO Error", ".SCH cannot be edited")
		else:
			#data_test_dump = f.readlines()[0]
			f.close()

		if "Part\#,PartType,FarnellLink,MouserLink,DigiKeyLink" or "Part\#;PartType;FarnellLink;MouserLink;DigiKeyLink" in data_test_dump:
			#this is a bug waiting to happen and not compatible with the FieldKeywords.conf 
			#verify it conforms to KiCAD Partslist-editor specs
			if openCSVFile.getComponents():
				openCSVFile.deleteContents()

			f = open(filename)

			openCSVFile.setContents(f.readlines())

			if openCSVFile.generateCSVComponents():
				messagebox.showerror("Incorrect Fileformat", "The file is neither comma separated nor semicolon separated")
			else:
				statusLabel['text'] = "Import: " + str(root.filename) + " complete" + "\n" +  str(openCSVFile.getNumberOfComponents()) + " components were imported"

			f.close()

		else:
			messagebox.showerror("FileParseError", "This is not a valid CSV document.")

	else:
		if filename:
			messagebox.showerror("FileParseError", "This is not a valid CSV document.")

	
def BuildNewSCH():
	initialDirectory = root.initialDirectory
	if mainFile.getComponents() and openCSVFile.getComponents():
		print(root.SCHFILELAST)
		savePath = filedialog.asksaveasfilename(initialfile = root.SCHFILELAST, filetypes = (("KiCAD Schematic File", ".sch"),("All Files",".*")))
		
		if savePath:
			if mainFile.ModifyNewSCHFile(0,openCSVFile,savePath):
				messagebox.showerror("File IO Error", ".SCH cannot be edited")
			else:
				statusLabel['text'] = str(savePath) + " updated with new field values"
	else:
		if mainFile.getComponents():
			messagebox.showerror("Processing Error", "No CSV File Loaded")
		elif openCSVFile.getComponents():
			messagebox.showerror("Processing Error", "No SCH File Loaded")
		else:
			messagebox.showerror("Processing Error", "No Files Loaded")
			
			
def CleanMemory():
	mainFile.deleteContents()
	openCSVFile.deleteContents()
	statusLabel['text'] = "Memory cleared \n All stored components deleted!"

def showAboutDialog():
	messagebox.showinfo("About KiCad Partslist Editor", "Use this tool to comfortably modify many parts fields in your favourite spreadsheet programm (e.g. LibreOffice Calc)\n" +
						"Written by BPJWES\n" +
						"https://github.com/BPJWES/KiCAD_Partslist_editor")

root = Tk()

root.initialDirectory = ""
root.configure(background='white')
root.title("KiCad Partslist Editor")
root.bind("<Escape>", lambda e: e.widget.quit())
background_image = PhotoImage(file="KICAD_PLE.png")
background = Label(root, image=background_image, bd=0)
background.grid(row = 0, column = 0, columnspan = 3, rowspan = 1, padx = 5, pady = 5)
ReadSettings()


b = ttk.Button(root, text="Load Schematic", command=OpenFile)
b.grid(row = 1, column = 0, columnspan = 1, rowspan = 1, padx = 5, pady = 5, )

g = ttk.Button(root, text="Save Schematic", command=BuildNewSCH)
g.grid(row = 2, column = 0, columnspan = 1, rowspan = 1, padx = 5, pady = 5)


c = ttk.Button(root, text="Export CSV", command=GenerateCSV)
c.grid(row = 1, column = 1, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

f = ttk.Button(root, text="Import CSV", command=loadCSV)
f.grid(row = 2, column = 1, columnspan = 1, rowspan = 1, padx = 5, pady = 5)


d = ttk.Button(root, text="List Parts", command=listParts)
d.grid(row = 1, column = 2, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

e = ttk.Button(root, text="Sort Parts", command=sortParts)
e.grid(row = 2, column = 2, columnspan = 1, rowspan = 1, padx = 5, pady = 5)


b = ttk.Button(root, text="About", command=showAboutDialog)
b.grid(row = 3, column = 2, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

h = ttk.Button(root, text="Clear Component Memory", command=CleanMemory)
h.grid(row = 3, column = 1, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

#i = ttk.Button(root, text="Exit", command=Break)
#i.grid(row = 5, column = 2, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

statusLabel = ttk.Label(root, text="Start by loading a KiCad schematic file...")
statusLabel['background'] = "white"
statusLabel.grid(row = 4, column = 0, columnspan = 3, rowspan = 1, padx = 5, pady = 5)


mainloop()
