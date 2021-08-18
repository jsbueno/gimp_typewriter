# gimp_typewriter

GIMP 2.x Python Plug-in to "type in" color strokes, mimicking a type-writter. 

To install: copy the ".py" file into a GIMP plug-ins folder (check
for the folder location in edit->preferences->folder inside GIMP). On
Linux and Mac, change the file permissions so that it is executable.

Once installed, upon starting GIMP, the "typewriter" option
will show up on the filters menu. When you click on it, a
small dialog box shows up with some sliders.

The idea is that you should focus on the inpuit area on the
plug-in dialog, and then, whatever you type is rendered
into the open GIMP image, which will show a small selection area
as the "target". This target will move left-to-right with each letter,
and to the next lower line when `<enter>` is typed, simulating
moving a typewriter to the next line.

The "raw" translation of letters into pixels is what makes for 
the "artistic factor", in ways that the clean text-editing functionality
in GIMP can't do. 

The sliders on the dialog allow one to control font-size, color
variations, how blurry, and text-deviation from the base line,
for added "vintage bonus". 
