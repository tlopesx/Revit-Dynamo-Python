# ------------------------------------------------------------ Imports ------------------------------------------------------------- #
import math, sys, clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitServices')
clr.AddReference('Microsoft.Office.Interop.Excel')
sys.path.append('.\BuroEhring')

import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *
from System.Collections.Generic import *

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
# ---------------------------------------------------------------------------------------------------------------------------------- #
import BE_REVIT

def getStructuralFraming():
    structuralFraming = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements())
    BE_structuralFraming = []
    for framing in structuralFraming:
        BE_structuralFraming.append(BE_REVIT.BE_Beam(framing))
    return BE_structuralFraming

def getStructuralFramingTypes():
    structuralFramingTypes = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_StructuralFraming).OfClass(FamilySymbol).WhereElementIsElementType())
    structuralFramingNames = list(map(lambda elementType : elementType.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(), structuralFramingTypes))
    return structuralFramingTypes, structuralFramingNames

def getStructuralColumns():
    structuralColumns = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements())
    BE_structuralColumns = []
    for column in structuralColumns:
        BE_structuralColumns.append(BE_REVIT.BE_Column(column))
    return BE_structuralColumns

def getStructuralColumnTypes():
    structuralColumnTypes = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_StructuralColumns).OfClass(FamilySymbol).WhereElementIsElementType())
    structuralColumnNames = list(map(lambda elementType : elementType.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(), structuralColumnTypes))
    return structuralColumnTypes, structuralColumnNames

def getAreaLoads():
    areaLoads = DB.FilteredElementCollector(doc).OfClass(DB.Structure.AreaLoad).ToElements()
    BE_areaLoads = []
    for load in areaLoads:
        BE_areaLoads.append(BE_REVIT.BE_Area_Load(load))
    return BE_areaLoads