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
import BE_COLLECTORS

beamTypes, beamTypeNames = BE_COLLECTORS.getStructuralFramingTypes()
columnTypes, columnNames = BE_COLLECTORS.getStructuralColumnTypes()

def changeBeamType(structuralMember, selectedElement):
    index = beamTypeNames.index(selectedElement)
    structuralMember.beam_shape = beamTypes[index]

def changeAllBeamTypes(structuralMemberList, selectedElement):
    for member in structuralMemberList:
        changeBeamType(member, selectedElement)
        # print('Updating {} to be a {}. This beam is a {}'.format(member.Name, selectedElement, member.Symbol.Category.Name))
		
def getGirders(structuralMemberList):
    girders = filter(lambda member: str(member.beam_structural_usage) == "Girder", structuralMemberList)
    BE_Girders = []
    for girder in girders:
        girder = girder.to_girder()
        BE_Girders.append(girder)
    return BE_Girders

def getJoists(structuralMemberList):
    joists = filter(lambda member: str(member.beam_structural_usage) == "Joist", structuralMemberList)
    BE_Joists = []
    for joist in joists:
        joist = joist.to_joist()
        BE_Joists.append(joist)
    return BE_Joists

def getPolygonVerticesFromAreaLoad(areaLoad):
    vertices = []
    # Gets curves from area loads
    loop = areaLoad.GetLoops()
    assert len(loop) == 1, "Donut shaped area loads not supported at the moment..."
    curves = list(loop[0].GetEnumerator())
    
    # Iterates through list of curves
    for curve in curves:
        startPoint = curve.GetEndPoint(0)
        endPoint = curve.GetEndPoint(1)
        if startPoint not in vertices:
            vertices.append(startPoint)
        if endPoint not in vertices:
            vertices.append(endPoint)
    # Returns new list of vertices
    return vertices
