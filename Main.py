# ------------------------------------------------------------ Imports ------------------------------------------------------------- #
import math, sys, clr, os

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitServices')
clr.AddReference('Microsoft.Office.Interop.Excel')
sys.path.append('.\BuroEhring')

import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

import BE_COLLECTORS, BE_STRUCTURE, BE_TRANSACTIONS

# Get all structural framing members
listOfBeams = BE_COLLECTORS.getStructuralFraming()
listOfColumns = BE_COLLECTORS.getStructuralColumns()

BE_TRANSACTIONS.useTransaction(lambda: BE_STRUCTURE.changeAllBeamTypes(listOfBeams, 'W12X40'))

beam = listOfBeams[0]
try:
	beam.calculate_supports(listOfBeams, listOfColumns)
except Exception,e:
	print(str(e))

#BE_TRANSACTIONS.useTransaction(lambda: BE_STRUCTURE.changeBeamType(beam, 'W44X335'))

listOfAreas = BE_COLLECTORS.getAreaLoads()
areaload = listOfAreas[0]

try:
	areaload._find_supporting_beams(listOfBeams)
	areaload._calculate_beam_tributary_area()
except Exception as e:
	print(e)

BE_TRANSACTIONS.useTransaction(lambda: BE_STRUCTURE.changeBeamType(areaload.supportingBeams[0], 'W44X335'))








# notes:
# get all beams
# we want to create a new class for our beams that will be able to calculate tributary area and length to calculate maximum moment. Method to update beam to proper sizes.
# class for beams that inherits from beams. Receives beams and uses them to calculate maximum moment.
# class to size from load. Takes in material and loads applied to beam. Looks up in corresponding load table the member we need.