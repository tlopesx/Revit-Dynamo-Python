# Buro Ehring - Structural Analysis for Revit

## Introduction

This project is written in Python, specifically designed to work with IronPython and RevitAPI. Its primary function is to identify the tributary areas for each structural member in a Revit model and preliminarily size them based on AISC standards.

## Prerequisites

- Autodesk Revit (Tested with Revit 2021)
- Revit Python Shell
- IronPython
- Microsoft Office Interop Excel (Optional)

## Installation

1. Run `COPY-BE.bat` to copy the modules into the appropriate Revit directory.
2. Copy the `Main.py` file into the Revit Python Shell in Revit.
3. Execute the script.

## Modules

### BE_AISC
Handles AISC beam initialization and properties.

### BE_GEOMETRY
Defines geometrical classes like Points, Lines, and Planes, and also includes utility functions for geometric calculations.

### BE_COLLECTORS
Responsible for collecting structural elements and their types, such as beams, columns, and area loads.

### BE_STRUCTURE
Defines classes for Columns, Beams, and Area Loads, and also includes methods for structural calculations.

### BE_TRANSACTIONS
Manages Revit transactions. Wraps function calls in a Revit transaction.

## Main File Overview

The `main` file serves as the entry point to the application. While it may appear minimalistic, it orchestrates the necessary functions and transactions to carry out the structural analysis.

### Sample Code Explanation
1. The script begins by importing all required libraries and modules.
2. It then initializes the Autodesk Revit's Document and UI Document for the current session.
3. `BE_COLLECTORS.getStructuralFraming()` and `BE_COLLECTORS.getStructuralColumns()` are invoked to obtain the structural elements present in the Revit model.
4. A Revit transaction is used to change all the beam types.
5. Individual beam supports are calculated.
6. Area loads are collected and their supporting beams are identified.
7. Tributary areas for beams are calculated based on the area loads.

```python
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

listOfAreas = BE_COLLECTORS.getAreaLoads()
areaload = listOfAreas[0]

try:
	areaload._find_supporting_beams(listOfBeams)
	areaload._calculate_beam_tributary_area()
except Exception as e:
	print(e)

BE_TRANSACTIONS.useTransaction(lambda: BE_STRUCTURE.changeBeamType(areaload.supportingBeams[0], 'W44X335'))
```

**Note**: The script is still under development and has been tested for compatibility with Revit 2021. Please proceed with caution.
