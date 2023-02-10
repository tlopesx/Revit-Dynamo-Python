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
import BE_GEOMETRY

class BE_Column(object):
    def __init__(self, revitColumn):
        self.revitColumn = revitColumn
        self.supports = set() # Dictionary with beam ID and location along beam
        self.supporting = set() # Dictionary with beam ID and location along beam

    @property
    def column_curve(self):    
        curve = self.revitColumn.GetAnalyticalModel().GetCurve() 
        return BE_GEOMETRY.BE_Line_Factory.createLineFromRevitLine(curve)

    @property
    def column_length(self):
        return BE_GEOMETRY.getLength(self.column_curve)

    @property
    def column_shape(self):
        return self.revitColumn.Symbol

    @column_shape.setter
    def column_shape(self, new_column):
        self.revitColumn.Symbol = new_column
        return

    @property
    def column_center(self):
        return BE_GEOMETRY.getCenterPoint(self.column_curve)


    @property
    def column_top(self):
        topAndBottom = BE_GEOMETRY.getTopAndBottom(self.column_curve)
        return topAndBottom[0]

    @property
    def column_bottom(self):
        topAndBottom = BE_GEOMETRY.getTopAndBottom(self.column_curve)
        return topAndBottom[1]

    @property
    def column_material(self):
        #do stuff
        pass

class BE_Beam(object):
    def __init__(self, revitBeam):
        self.revitBeam = revitBeam
        self.beam_supports = set() # Dictionary with beam ID and location along beam
        self.column_supports = set() # Dictionary with column ID and location along beam
        self.supporting = set() # Dictionary with beam ID and location along beam

    @property
    def beam_curve(self):    
        curve = self.revitBeam.GetAnalyticalModel().GetCurve() 
        return BE_GEOMETRY.BE_Line_Factory.createLineFromRevitLine(curve)

    @property
    def beam_length(self):
        return BE_GEOMETRY.getLength(self.beam_curve)

    @property
    def beam_shape(self):
        return self.revitBeam.Symbol

    @beam_shape.setter
    def beam_shape(self, new_beam):
        self.revitBeam.Symbol = new_beam
        return

    @property
    def beam_center(self):
        return BE_GEOMETRY.getCenterPoint(self.beam_curve)

    @property
    def beam_material(self):
        #do stuff
        pass

    @property
    def beam_structural_usage(self):
        return str(self.revitBeam.StructuralUsage)

    def clean_out_supports(self):
        self.beam_supports = set()
        self.column_supports = set()
        self.supporting = set()

    def calculate_supports(self, otherBeams, columns):
        self.clean_out_supports()
        for column in columns:
            intersectionType, IRA = self.beam_curve.Intersection(column.column_curve)
            if intersectionType == SetComparisonResult.Overlap:
                for IR in IRA.GetEnumerator():
                    U = round(self.beam_curve.revitLine.ComputeNormalizedParameter(IR.UVPoint.U),3)
                    self.column_supports.add(BE_SupportingMember(column, U))

        for beam in otherBeams:
            if beam.revitBeam != self.revitBeam:
                intersectionType, IRA = self.beam_curve.Intersection(beam.beam_curve)
                if intersectionType == SetComparisonResult.Overlap:
                    for IR in IRA.GetEnumerator():
                        U = round(self.beam_curve.revitLine.ComputeNormalizedParameter(IR.UVPoint.U),3)
                        if U != 0 and U != 1:
                            self.supporting.add(BE_MemberToSupport(beam, U))
                        elif U not in list(map(lambda column_support: column_support.locationAlongBeam, self.column_supports)):
                            self.beam_supports.add(BE_SupportingMember(beam, U))

        print("New Beam!")
        print("\tColumn Supports: %d" % len(self.column_supports))
        print("\tBeam Supports: %d" % len(self.beam_supports))
        print("\tSupporting: %d" % len(self.supporting))

class BE_Area_Load(object):
    def __init__(self, revitAreaLoad):
        self.revitAreaLoad = revitAreaLoad
        self.supportingBeams = []
        self.adjacentBeamsLeft = []
        self.adjacentBeamsRight = []

    @property
    def loops(self):
        return self.revitAreaLoad.GetLoops()
        
    @property
    def area_vertices(self):
        all_vertices = BE_GEOMETRY.getVerticesFromLoop(self.loops)
        return all_vertices

    @property
    def has_multiple_loops(self):
        if len(self.loops) == 1:
            return False
        else:
            return True

    @property
    def orientation(self):
        #get orientation from type
        orientation = 0
        return orientation
    
    def _find_supporting_beams(self, beams):
        self.supportingBeams = []
        for beam in beams:
            if(BE_GEOMETRY.pointInPolygon(self.area_vertices, beam.beam_curve.GetEndPoint(0))):
                if(BE_GEOMETRY.pointInPolygon(self.area_vertices, beam.beam_curve.GetEndPoint(1))):
                    if(BE_GEOMETRY.getOrientation(beam.beam_curve)) == self.orientation:
                        self.supportingBeams.append(beam)

    def _calculate_beam_tributary_area(self):
        for beam in self.supportingBeams:

            beamPlane = BE_GEOMETRY.BE_Plane_Factory.createPlaneFromLine(beam.beam_curve)     
            leftAdjacentBeams, rightAdjacentBeams = [], []
            
            for otherBeam in self.supportingBeams:
                if otherBeam != beam:
                    UV = beamPlane.transformCartesianPoint(otherBeam.beam_center)
                    U = UV.X
                    if U > 0:
                        leftAdjacentBeams.append(otherBeam)
                    elif U < 0:
                        rightAdjacentBeams.append(otherBeam)
            try:
                if leftAdjacentBeams is not None:
                    leftAdjacentBeam = self._get_adjacent_beams(beam, leftAdjacentBeams)
                    if leftAdjacentBeam is not None:
                        self.adjacentBeamsLeft.append(leftAdjacentBeam)
                        self._get_trib_areas(beam, leftAdjacentBeam)
                    else:
                        self.adjacentBeamsLeft.append("")
                else:
                    self.adjacentBeamsLeft.append("")
                
                if rightAdjacentBeams is not None:
                    rightAdjacentBeam = self._get_adjacent_beams(beam, rightAdjacentBeams)
                    if rightAdjacentBeam is not None:
                        self.adjacentBeamsRight.push(rightAdjacentBeam)
                        self._get_trib_areas(beam, rightAdjacentBeam)
                    else:
                        self.adjacentBeamsRight.append("")
                else:
                    self.adjacentBeamsRight.append("")

            except Exception as e:
               print("Failed calculating beam tributary area.") 
               print(e)

    def _get_adjacent_beams(self, beam, adjacentBeams):
        try:
            beamOrientation = BE_GEOMETRY.getOrientation(beam.beam_curve)
            try:
                # Filter out curves that are coincident with the beam
                adjacentBeams = filter(lambda otherBeam: \
                                    round(min((BE_GEOMETRY.getDistance(beam.beam_curve.GetEndPoint(0), otherBeam.beam_curve.GetEndPoint(0)) + BE_GEOMETRY.getDistance(beam.beam_curve.GetEndPoint(1), otherBeam.beam_curve.GetEndPoint(1))),
                                        (BE_GEOMETRY.getDistance(beam.beam_curve.GetEndPoint(0), otherBeam.beam_curve.GetEndPoint(1)) + BE_GEOMETRY.getDistance(beam.beam_curve.GetEndPoint(1),otherBeam.beam_curve.GetEndPoint(0)))),3) !=0, adjacentBeams)
            except:
                print("Failed to filter our coincident beams")
                print(e)           
            
            
            try:
                # Filter out curves that are perpendicular to the beam
                adjacentBeams = filter(lambda otherBeam: ((BE_GEOMETRY.getOrientation(otherBeam.beam_curve) != (beamOrientation + (math.pi)/2)) or (BE_GEOMETRY.getOrientation(otherBeam.beam_curve) != (beamOrientation - (math.pi)/2))), adjacentBeams)
            except Exception as e:
                print("Failed filtering perpendicular curves")
                print(e)

            try:
                # Sort beams by distance from beam
                adjacentBeams.sort(key = lambda adjacentBeam : adjacentBeam.beam_curve.closestDistanceToOtherLine(beam.beam_curve))
            except Exception as e:
                print("Failed sorting by distance")
                print(e)

            if len(adjacentBeams) != 0:
                try:
                    # Find distance to closest beam

                    closestDistance = adjacentBeams[0].beam_curve.closestDistanceToOtherLine(beam.beam_curve)
                    print("The closest beam is %d units away" % closestDistance)
                    # Get all beams that are that distance away
                    adjacentBeams = filter(lambda otherBeam: otherBeam.beam_curve.closestDistanceToOtherLine(beam.beam_curve) == closestDistance, adjacentBeams)
                
                except Exception as e:
                    print("Failed getting closest beams")
                    print(e)

                try:
                    # Compare adjacencies - this needs work
                    adjacentBeams.sort(key = lambda otherBeam: \
                                    min((BE_GEOMETRY.getDistance(beam.beam_curve.GetEndPoint(0), otherBeam.beam_curve.GetEndPoint(0)) + BE_GEOMETRY.getDistance(beam.beam_curve.GetEndPoint(1), otherBeam.beam_curve.GetEndPoint(1))), \
                                        (BE_GEOMETRY.getDistance(beam.beam_curve.GetEndPoint(0), otherBeam.beam_curve.GetEndPoint(1)) + BE_GEOMETRY.getDistance(beam.beam_curve.GetEndPoint(1),otherBeam.beam_curve.GetEndPoint(0)))))
                except Exception as e:
                    print("Failed sorting by adjacency. This is the lambda!!")
                    print(e)

                return adjacentBeams[0]
            
            else:
                return None
        
        except Exception as e:
            print("Failed to get adjacent beams")
            print(e)

    def _get_trib_areas(self, beam, adjacentBeam):

        try:
            # Essentially tween
            edge1 = beam.beam_curve.revitLine
            edge2 = BE_GEOMETRY.BE_Line_Factory.createLineFromEndPoints(beam.beam_curve.GetEndPoint(0), adjacentBeam.beam_curve.GetEndPoint(0)).revitLine
            edge3 = adjacentBeam.beam_curve.revitLine
            edge4 = BE_GEOMETRY.BE_Line_Factory.createLineFromEndPoints(beam.beam_curve.GetEndPoint(1), adjacentBeam.beam_curve.GetEndPoint(1)).revitLine

            edges = clr.Reference[IList[Curve]]([edge1, edge2, edge3, edge4])
            edges = edges.Value
            DB.CurveLoop.Create(edges)
        
        except Exception as e:
            print("\nFailed to create a curve loop from edges")
            print(e)
        
        finally:
            print("\nBeam start point:" + str(beam.beam_curve.GetEndPoint(0)))
            print("Beam end point:" + str(beam.beam_curve.GetEndPoint(1)))
            print("AdjacentBeam start point:" + str(adjacentBeam.beam_curve.GetEndPoint(0)))
            print("AdjacentBeam end point:" + str(adjacentBeam.beam_curve.GetEndPoint(1)))

        return

class BE_MemberToSupport(object):
    def __init__(self, memberToSupport, locationAlongBeam):
        self.memberToSupport = memberToSupport
        self.locationAlongBeam = locationAlongBeam

    def __str__(self):
        description = "This member supports a %s at %f" % (self.memberToSupport.beam_shape, self.locationAlongBeam)
        return description

    def __eq__(self, other):
        if self.memberToSupport == other.memberToSupport and self.locationAlongBeam == other.locationAlongBeam:
            return True
        else:
            return False

class BE_SupportingMember(object):
    def __init__(self, supportingMember, locationAlongBeam):
        self.supportingMember = supportingMember
        self.locationAlongBeam = locationAlongBeam
    
    def __str__(self):
        description = "This member supports a %s at %f" % (self.supportingMember.beam_shape, self.locationAlongBeam)
        return description

    def __eq__(self, other):
        if self.supportingMember == other.supportingMember and self.locationAlongBeam == other.locationAlongBeam:
            return True
        else:
            return False

class BE_Load_Points(object):
    def __init__(self, location, parameter, force):
        self.location = location
        self.parameter = parameter
        self.force = force

    @property
    def X(self):
        return self.location.X

    @property
    def Y(self):
        return self.location.Y

    @property
    def Z(self):
        return self.location.Z

    def add_force(self, force):
        self.force += force
        print("Trying to update the force. New force is {}".format(self.force))
        return self.force

    def __repr__(self):
        return 'Location: ({},{},{}) Force Applied: {}'.format(self.X, self.Y, self.Z, self.force)