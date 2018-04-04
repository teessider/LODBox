from __future__ import print_function
# import sys
import fbx
import FbxCommon
import samples.ImportScene.DisplayLodGroup

filepaths = {'Attributes': "Sphere_Attr.fbx",
             'lodGroup': "Sphere_lodGroup.fbx",
             'Group_lods': "Sphere_group_lods.fbx"}  # Hardcoded for now

# FbxCommon containers some helper functions to get rid of some of the boilerplate
manager, scene = FbxCommon.InitializeSdkObjects()
global_settings = scene.GetGlobalSettings()  # type: fbx.FbxGlobalSettings

fbx_scene_2 = FbxCommon.LoadScene(manager, scene, filepaths['lodGroup'])
# fbx_scene_1 = FbxCommon.LoadScene(manager, scene, filepaths['Group_lods'])
root_node = scene.GetRootNode()  # type: fbx.FbxNode

# 1st method of getting high-level scene nodes
# Using root_node.GetChildCount(True) (returns number of children with recursion)
# to get all scene nodes returns None for grandchildren and lower
scene_nodes = [root_node.GetChild(i) for i in range(0, root_node.GetChildCount())]
print("Total number of nodes in the scene are: {}\n"
      "The root node is: {}".format(root_node.GetChildCount(True), root_node.GetName()))
print(global_settings.GetSystemUnit().GetScaleFactorAsString())
print(global_settings.GetOriginalUpAxis(), "== Z-Up")
for node in scene_nodes:
    node_attr = node.GetNodeAttribute()
    for x in range(0, node.GetChildCount()):
        child = node.GetChild(x)
        scene_nodes.append(child)
    if isinstance(node_attr, fbx.FbxLODGroup):
        samples.ImportScene.DisplayLodGroup.DisplayLodGroup(node)
        # print(node.GetName(), "I'm a LODGroup")
    elif isinstance(node_attr, fbx.FbxMesh):
        print(node.GetName(), "I'm a mesh!")
    else:
        print(node.GetName(), type(node_attr))


# 2nd method of getting scene nodes
# scene_nodes_2 = []
# print("Total Number of nodes in scene are: {}".format(root_node.GetChildCount(True)))
# for i in range(0, root_node.GetChildCount(True)):
#     child = root_node.GetChild(i)
#     scene_nodes_2.append(child)
# for node in scene_nodes_2:
#     if node:
#         print(node.GetName(), type(node), "2nd Method")

