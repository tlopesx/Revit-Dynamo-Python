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

import Microsoft.Office.Interop.Excel as Excel

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
# ---------------------------------------------------------------------------------------------------------------------------------- #

# Open AISC Spreadsheet
def initializeAISC():
    excel = Excel.ApplicationClass()
    workbook = excel.Workbooks.Open("C:\\Users\\tlope\\Desktop\\Revit Dynamo Python\\AISC Database\\Database-v15.0.xlsx")
    sheet = workbook.Sheets("Database v15.0")
    return workbook, sheet

def closeAISCSreadsheet(workbook):
    excel = Excel.ApplicationClass()
    excel.Workbooks.Close()

# Opens AISC Spreadsheet and extracts all beams
def getAllAISCBBeams():
    AISC_Beams = []
    sheet = initializeAISC()
    
    totalRows = sheet.UsedRange.Rows.Count
    totalColumns = sheet.UsedRange.Columns.Count
    
    for row in range(2,totalRows):
        row = row + 1
        excelRow = sheet.Range(sheet.Cells(row,1),sheet.Cells(row, totalColumns))
        aiscBeam = AISC_Beam(excelRow)
        AISC_Beams.append(aiscBeam)

    return AISC_Beams

def initializeAISCBeams():
    initializeAISC()
    beams = getAllAISCBBeams()
    return beams

#Extract Data from AISC Spreadsheet to Store Beam Objects
class AISC_Beam():
    def __init__(self, excelRow):
        self._excelRow = excelRow

    @property
    def name(self):
        return self._excelRow.Cells[1, 2].Value()

    @property
    def depth(self):
        return self._excelRow.Cells[1,7].Value()

    @property
    def nominal_depth(self):
        return math.ceil(self.depth)

    @property
    def moment_inertia_x(self):
        return self._excelRow.Cells[1,39].Value()
    
    @property
    def moment_inertia_y(self):
            return self._excelRow.Cells[1,43].Value()

    @property
    def plastic_section_modulus_x(self):
        return self._excelRow.Cells[1,40].Value()
        
    @property
    def plastic_section_modulus_y(self):
        return self._excelRow.Cells[1,44].Value()

    @property
    def elastic_section_modulus_x(self):
        return self._excelRow.Cells[1,41].Value()
    
    @property
    def elastic_section_modulus_y(self):
        return self._excelRow.Cells[1,45].Value()