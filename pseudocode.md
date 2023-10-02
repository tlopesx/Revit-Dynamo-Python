**Beam:**  
- Supports = []   --------	> parents  
- Supporting = [] -------	> children  
- Loads = [] --------------	> (areaID, beamID?, locationOnBeam, vector)  
- *Calculate loads() ------->	creates supports and supporting lists*  
- Distribute Load(): ---- > calculates load from loads to apply to supports	 

**Area Loads:**  
- Big Shape: Boundary Curves  
- Magnitude: Weight in PSF  
- Orientation: Angle  
- Supporting Beams: which beams are supporting the area load.  
- CalculateLoads(): finds supporting beams, gets adjacencies  
  - Orientation  
  - And point in polygon  
- Distribute Load() : calculates load from loads to apply to supports  


**Calculate**
- Get area loads. Figure out which beams directly support the area loads.    
- Create load to add to those members.  
- Get members supporting those members.  
- Create load to add to those members.  
- Get members supporting those members.  
- Create load to add to those members.  
