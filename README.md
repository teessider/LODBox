# README
*testy_mctestface.py* is the live test script i'm working with<br>

Below are my running notes for doing this whole thing. These are LIVE notes.<br>
Please be aware these may not make sense to anybody but me but perhaps they can be useful.<br>
(Perhaps this might get formatted properly!)


## Terminology
| FBX SDK                                  | Maya             |
|------------------------------------------|------------------|
| Node - FbxNode()                         | "Transform" Node |
| 	NodeNode Attribute - FbxNodeAttribute() | "Shape"          |
| material.DiffuseColor                    | material.color   |
| Node - FbxNode() with *FbxNull* property | "empty" Group    |

Nodes can be parented just like in Maya<br>
Material attributes might have different names in the FBX SDK<br>

## Maya > Max
- UV sets are passed as user-defined properties on mesh (NOT CUSTOM ATTRIBUTE) if in LOD group
- If exported as a LodGroup then custom Attributes are lost (at least when imported into 3ds Max)
    - EDIT: Not lost - just not accessible in the 3ds Max UI (there is an error on import actually in MAXScript listener)
- If Max keeps UV set user-defined property, would be cool to clean up on import actually to remove this from custom attributes.

## FBX SDK
- LODGroups can be created (*fbx.FbxLODGroup.Create(FbxManager, name)*) from existing nodes
- *SetDisplayLevel()* in FbxLODGroup arguments: (index, Display Level as int)
  - Display Level is an enum in C++ but it has been converted to int in Python FBX:
    - UseLOD = 0
    - Show = 1
    - Hide = 2
- Maya makes the LODGroup Node attribute name == "" (AKA None)
- Max makes the LODGroup Node attribute name == Node Name (Also it doesn't matter what the name is)
- BOTH: MinMaxDistance == False by default
- BOTH: IsWorldSpace == False by default (True in Maya test file)
- FbxNode.AddChild(child) - This doesn't have any order to it so if creating from scratch, it is worth ordering before hand.


## Features/Goals:
- Create LOD Groups outside of Max/Maya
- Organize LOD Groups
- Export/Import existing LOD Groups
- Extract LODs/Reimport them
- Interface with other tools
- Work inside of Max/Maya too? (On Import and On Export)