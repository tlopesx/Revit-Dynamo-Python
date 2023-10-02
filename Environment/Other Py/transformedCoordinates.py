import math
import statistics

class BE_Plane():
    def __init__(self, origin, rotationAngle = 0):
        self.origin = origin
        self.rotationAngle = rotationAngle
        self.X = origin[0]
        self.Y = origin[1]

    def transformCartesianPoint(self, pointToTransform):
        angle = getAngleBetweenLineAndPlaneAxis(self.origin, pointToTransform, self, "Y")
        distance = getDistance(self.origin, pointToTransform)

        transformedX = math.cos(angle) * distance
        transformedY = math.sin(angle) * distance

        transformedCoordinates = (transformedX, transformedY)
        return transformedCoordinates


class BE_Plane_Factory():
    @staticmethod
    def createPlane(origin, rotationAngle):
        return BE_Plane(origin, rotationAngle)

    @staticmethod
    def createPlaneFromCurve(curveStart, curveEnd):
        midPoint = getMidpoint(curveStart, curveEnd)
        rotationAngle = getAngleBetweenLineAndPlaneAxis(midPoint, curveEnd)
        return BE_Plane(midPoint, rotationAngle)


def getAngleBetweenLineAndPlaneAxis(start, end, workingPlane=BE_Plane_Factory.createPlane((0,0),0), axis="X"):
    assert type(start) == tuple and len(start) == 2, "Start point must be a tuple of length 2"
    assert type(end) == tuple and len(end) == 2, "End point must be a tuple of length 2"
    assert axis == "X" or axis == "Y", "Reference axis must be 'X' or 'Y'"
    
    planeAngle = workingPlane.rotationAngle
    if axis == "X":
        lineAngle = math.atan((end[0] - start[0]) / (end[1] - start[1]))
    if axis == "Y":
        lineAngle = math.atan((end[1] - start[1]) / (end[0] - start[0]))      
    return planeAngle + lineAngle


def getDistance(start, end):
    assert type(start) == tuple and len(start) == 2, "Start point must be a tuple of length 2"
    assert type(end) == tuple and len(end) == 2, "End point must be a tuple of length 2"
    distance = math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
    return distance


def getMidpoint(start, end):
    assert type(start) == tuple and len(start) == 2, "Start point must be a tuple of length 2"
    assert type(end) == tuple and len(end) == 2, "End point must be a tuple of length 2"

    midX = statistics.mean([start[0], end[0]])
    midY = statistics.mean([start[1], end[1]])
    return (midX, midY)


# Testing the script
curveStart = (55,93)
curveEnd = (13,48)
workingPlane = BE_Plane_Factory.createPlaneFromCurve(curveStart, curveEnd)
testPoint = (85,79)
point = workingPlane.transformCartesianPoint(testPoint)
print(point)






