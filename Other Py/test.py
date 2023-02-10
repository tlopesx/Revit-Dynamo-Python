def pointInPolygon(polygon, point):


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
    for index in range(len(polygon.vertices)):

        #Get segment start and end points
        if index != polygon.vertices:
            segmentX = (polygon.vertices[index].X, polygon.vertices[index+1].X)
            segmentY= (polygon.vertices[index].Y, polygon.vertices[index+1].Y)

        else:
            segmentX = (polygon.vertices[index].X, polygon.vertices[0].X)
            segmentY = (polygon.vertices[index].Y, polygon.vertices[0].Y)

        intersections = projectPointUpward(segmentX, segmentY, point, intersections)

    # If the number of intersections is even, the point is not in the polygon, return False
    if intersections % 2 == 0:
        return False
    else:
        return True

# Create transcation to update beams
useTransaction(lambda: changeBeamType(listOfBeams[0], 'W24X306', structuralElementTypeNames, structuralElementTypes))

#Iterate through beams
listOfBeams = []
listofBeamCurves[]
for beamNum, beam in enumerate(listOfBeams):

    listOfBeamCurves.append(beam.beam_curve)

    print("Beam Name: "),
    print(beam.Name),
    print("\tBeam Function: "),
    print(beam.StructuralUsage),
    print("\tCenter: "),
    print(getCenterPoint(beamCurve))

numOfBeams = len(listOfBeams)
print(numOfBeams)



# Pull out joists
joists = BE_STRUCTURE.getJoists(listOfBeams)

# Pull out girders
girders = BE_STRUCTURE.getGirders(listOfBeams)

# Get area loads
areaLoads = BE_COLLECTORS.getAreaLoads()
load = areaLoads[0]

for joist in joists:
    for girder in girders:
        girder.create_load_points(joist)





    # def to_joist(self):
    #     joist = BE_Joist(self.revitBeam)
    #     return joist

    # def to_girder(self):
    #     return BE_Girder(self.revitBeam)

# class BE_Joist(BE_Beam):
#     def __init__(self, revitBeam):
#         super(BE_Joist, self).__init__(revitBeam)
#         self.load_points = self.create_load_points()

#     # def create_load_points(self, spacing = 1):
#     #     numPoints= int(self.beam_length // spacing + 1)
#     #     load_points = []
#     #     for i in range(0, numPoints):
#     #         t =  i * spacing / self.beam_length
#     #         pointXYZ = self.beam_curve.Evaluate(t, True)
#     #         load_points.append(BE_Load_Points(BE_Point(pointXYZ.X, pointXYZ.Y, pointXYZ.Z), t, 0))
#     #     return load_points

#     # def apply_loads_to_points(self, load):
#     #     for load_point in self.load_points:
#     #         if BE_GEOMETRY.pointInPolygon(load.area_vertices, load_point):
#     #             load_point.add_force(load.revitAreaLoad.ForceVector1.Z)
#     #             print("Found point affected by load!")
#     #         else:
#     #             print("Point not affected by load...")
#     #     print(load_point)

#     # def print_load_points(self):
#     #     for point in self.load_points:
#     #         print(point)


# class BE_Girder(BE_Beam):
#     def __init__(self, revitBeam):
#         super(BE_Girder, self).__init__(revitBeam)
#         self.load_points = []

#     # def create_load_points(self, BE_Joist):
#     #     IRA = clr.Reference[IntersectionResultArray]()
#     #     intersectionType = self.beam_curve.revitBeam.IntersectBE_Joist.beam_curve, IRA)
#     #     if intersectionType == SetComparisonResult.Overlap:
#     #         for IR in IRA.GetEnumerator():
#     #             t = self.beam_curve.ComputeNormalizedParameter(IR.UVPoint.U)
#     #             pointXYZ = IR.XYZPoint
#     #             if round(t, 3) in list(map(lambda load_point: round(load_point.parameter,3), self.load_points)):
#     #                 print("Placeholder. Need to add reaction on girder here...")
#     #             else:
#     #                 self.load_points.append(BE_Load_Points(BE_Point(pointXYZ.X, pointXYZ.Y, pointXYZ.Z), t, 0))
