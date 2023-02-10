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

import math



class BE_Point(DB.XYZ):
    def __init__(self, X,Y,Z):
        super(BE_Point, self).__init__(X,Y,Z)

    def __eq__(self, other):
        if self.X == other.X and self.Y == other.Y and self.Z == other.Z:
            return True
        else:
            return False

    def __repr__(self):
        return '({},{},{})'.format(self.X, self.Y, self.Z)

class BE_Line(object):
    def __init__(self, line):
        self.revitLine = line

    def closestDistanceToOtherLine(self, other):
        try:
            CPPBTC = clr.Reference[IList[ClosestPointsPairBetweenTwoCurves]]([])
            self.ComputeClosestPoints(other, False, False, False, CPPBTC)
            closestPointsPair = BE_ClosestPointsPair(CPPBTC)
            distance =  closestPointsPair.distance
        except:
            midPoint = getCenterPoint(other)
            distance = self.revitLine.Distance(midPoint)
        return distance
        
    def GetEndPoint(self, param):
        return self.revitLine.GetEndPoint(param)

    def Intersection(self, other):       
        IRA = clr.Reference[IntersectionResultArray]()
        intersectionType = self.revitLine.Intersect(other.revitLine, IRA)
        return intersectionType, IRA
  
class BE_Line_Factory():
    @staticmethod
    def createLineFromEndPoints(start, end):
        line = DB.Line.CreateBound(start, end)
        BE_line = BE_Line(line)
        return BE_line

    @staticmethod
    def createLineFromRevitLine(line):
        BE_line = BE_Line(line)
        return BE_line

class BE_Plane():
    def __init__(self, origin, rotationAngle = 0):
        self.origin = origin
        self.rotationAngle = rotationAngle
        self.X = origin.X
        self.Y = origin.Y

    def transformCartesianPoint(self, pointToTransform):
        try:
            try:
                line = BE_Line_Factory.createLineFromEndPoints(self.origin, pointToTransform)
            except Exception as e:
                print("Origin: %s, PointToTransform: %s" % (self.origin, pointToTransform))
                print(e)
            else:
                angle = getAngleBetweenLineAndPlaneAxis(line, self, "Y") 
                distance = getDistance(self.origin, pointToTransform)

                transformedX = math.cos(angle) * distance
                transformedY = math.sin(angle) * distance

                transformedCoordinates = BE_Point(transformedX, transformedY, 0)
                return transformedCoordinates
        
        except Exception as e:
            print("Failed transforming cartesian coordiantes.")
            print(e)

class BE_Plane_Factory():
    @staticmethod
    def createPlane(origin, rotationAngle):
        return BE_Plane(origin, rotationAngle)

    @staticmethod
    def createPlaneFromLine(line):
        try:
            midPoint = getCenterPoint(line)
            rotationAngle = getAngleBetweenLineAndPlaneAxis(line)
            return BE_Plane(midPoint, rotationAngle)
        except Exception as e:
            print("Failed creating plane from line.")
            print(e)

class BE_ClosestPointsPair():
    def __init__(self, CPPBTC):
        self.CPPBTC = CPPBTC

    @property
    def distance(self):
        distance = 0
        enumerator = self.CPPBTC.GetEnumerator()
        while enumerator.GetNext():
            dist = enumerator.Current.Distance
            distance = min(distance, dist)
        return distance

def getVerticesFromLoop(loops):
    all_vertices = []
    for loop in loops:
        for l, line in enumerate(loop.GetCurveLoopIterator()):
            if l == 0:
                vertices = []
            # Get start point, add to vertices if not already in there
            start = BE_Point(line.GetEndPoint(0).X, line.GetEndPoint(0).Y, line.GetEndPoint(0).Z)
            if start not in vertices:
                vertices.append(start)
            # Get end point, add to vertices if not already in there
            end = BE_Point(line.GetEndPoint(1).X, line.GetEndPoint(1).Y, line.GetEndPoint(1).Z)
            if end not in vertices:
                vertices.append(end)
        # Add list of vertices to all_vertices list
        all_vertices.append(vertices)

    return all_vertices

def getTopAndBottom(verticalLine):
    '''Returns a tuple containing the top and bottom points of the verticalLine'''
    topAndBottom = (verticalLine.GetEndPoint(0), verticalLine.GetEndPoint(1))
    topAndBottom.sort(key = lambda point: point.Z, reverse=True)
    return topAndBottom

def getCenterPoint(line):
    start = line.GetEndPoint(0)
    end = line.GetEndPoint(1)
    return (start + end) / 2

def getLength(line):
    start = line.GetEndPoint(0)
    end = line.GetEndPoint(1)
    return start.DistanceTo(end)

def getOrientation(line):
    start = line.GetEndPoint(0)
    end = line.GetEndPoint(1)
    rad = math.atan((end.X - start.X) / (end.Y - start.Y))
    return math.fabs(round(math.degrees(rad)))

def pointInPolygon(vertexLists, point):

    def projectPointUpward(segmentX, segmentY, point, intersections):

        segmentstartX = segmentX[0]
        segmentendX = segmentX[1]

        segmentstartY = segmentY[0]
        segmentendY = segmentY[1]

        # Check if the testpoint falls between the range of values of X for the start and end of the segment
        if (segmentstartX < point.X < segmentendX or segmentendX < point.X < segmentstartX):
            
            # If it does, get the y coordinate of the intersection
            t = (point.X * segmentendX) / (segmentstartX - segmentendX)
            segmentIntersectY = (t * segmentstartY) + ((1 - t) * segmentendY)

            # If the y coordinate of the intersection is above the testpoint y, add 1 intersection
            if segmentIntersectY >= point.Y:
                intersections += 1
            
        # If the test point is at the start point of the segment or below it
        if (segmentstartX == point.X and segmentstartY >= point.Y):
            intersections += 1

        # If the segment is a vertical line and the segment is between the start and end points
        if (segmentstartX == segmentendX and (segmentstartY < point.Y <= segmentendY or segmentendY <= point.Y < segmentstartY)):
            intersections += 1

        return intersections

    # Delcare intersections to be 0
    intersections = 0

    # Loop through all of the segments of the polygon
    for vertices in vertexLists:

        for index in range(len(vertices)):
            #Get segment start and end points
            if index != len(vertices) - 1:
                segmentX = (vertices[index].X, vertices[index+1].X)
                segmentY= (vertices[index].Y, vertices[index+1].Y)

            else:
                segmentX = (vertices[index].X, vertices[0].X)
                segmentY = (vertices[index].Y, vertices[0].Y)

            intersections = projectPointUpward(segmentX, segmentY, point, intersections)

    # If the number of intersections is even, the point is not in the polygon, return False
    if intersections % 2 == 0:
        return False
    else:
        return True

def getAngleBetweenLineAndPlaneAxis(line, workingPlane=BE_Plane_Factory.createPlane(BE_Point(0,0,0),0), axis="X"):
    assert axis == "X" or axis == "Y", "Reference axis must be 'X' or 'Y'"
    
    start = line.GetEndPoint(0)
    end = line.GetEndPoint(1)
    
    planeAngle = workingPlane.rotationAngle
    if axis == "X":
        lineAngle = math.atan((end.X - start.X) / (end.Y - start.Y))
    if axis == "Y":
        lineAngle = math.atan((end.Y - start.Y) / (end.X - start.X))      
    return planeAngle + lineAngle

def getDistance(start, end):
    return start.DistanceTo(end)
