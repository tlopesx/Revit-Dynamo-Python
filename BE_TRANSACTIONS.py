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

def useTransaction(function):
    transaction = Transaction(doc, function.__name__)
    print("Starting Transaction...")
    transaction.Start()
    try:
        function()
    except Exception as e:
        transaction.RollBack()
        print("Transaction Failed...")
        print(e)
    else:
        transaction.Commit()
        print("Transaction Successful...")