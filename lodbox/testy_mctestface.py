from __future__ import print_function
import sys
import fbx
import FbxCommon

filepaths = {'Attributes': "Sphere_Attr.fbx",
             'lodGroups': "Sphere_lodGroup.fbx",
             'Group_lods': "Sphere_group_lods.fbx"}  # Hardcoded for now

# FbxCommon containers some helper functions to get rid of some of the boilerplate
manager, scene = FbxCommon.InitializeSdkObjects()

fbx_scene = FbxCommon.LoadScene(manager, scene, filepaths['lodGroups'])

root_node = scene.GetRootNode()  # type: fbx.FbxNode

# 1st method of getting high-level scene nodes
# Using root_node.GetChildCount(True) (returns number of children with recursion)
# to get all scene nodes returns None for grandchildren and lower
scene_nodes = [root_node.GetChild(i) for i in range(0, root_node.GetChildCount())]
print("Total number of nodes in the scene are: {}".format(root_node.GetChildCount(True)))
for node in scene_nodes:
    if node:
        print(node.GetName(), type(node))


# 2nd method of getting scene nodes
# scene_nodes_2 = []
# print("Total Number of nodes in scene are: {}".format(root_node.GetChildCount(True)))
# for i in range(0, root_node.GetChildCount(True)):
#     child = root_node.GetChild(i)
#     scene_nodes_2.append(child)
# for node in scene_nodes_2:
#     if node:
#         print(node.GetName(), type(node), "2nd Method")

