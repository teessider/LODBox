from __future__ import print_function
import fbx
import FbxCommon
from samples.ImportScene.DisplayUserProperties import DisplayUserProperties

filepaths = {'Attributes': "Sphere_Attr.fbx",
             'lodGroup': "Sphere_lodGroup.fbx",
             'lodGroup_Max': "Sphere_lodGroup_Max.FBX",
             'Group_lods': "Sphere_group_lods.fbx"}  # Hardcoded for now

# FbxCommon contains some helper functions to get rid of some of the boilerplate
manager, scene = FbxCommon.InitializeSdkObjects()
global_settings = scene.GetGlobalSettings()  # type: fbx.FbxGlobalSettings

fbx_scene_3 = FbxCommon.LoadScene(manager, scene, filepaths['lodGroup_Max'])
# fbx_scene_2 = FbxCommon.LoadScene(manager, scene, filepaths['lodGroup'])
# fbx_scene_1 = FbxCommon.LoadScene(manager, scene, filepaths['Group_lods'])

root_node = scene.GetRootNode()  # type: fbx.FbxNode

# 1st method of getting high-level scene nodes
# Using root_node.GetChildCount(True) (returns number of children with recursion)
# to get all scene nodes but returns None for grandchildren and lower
scene_nodes = [root_node.GetChild(i) for i in range(0, root_node.GetChildCount())]
print("Total number of nodes in the scene are: {}\n"
      "The root node is: {}\n"
      "Scene Units: {}\n{}: Z-UP".format(root_node.GetChildCount(True), root_node.GetName(), global_settings.GetSystemUnit().GetScaleFactorAsString(), global_settings.GetOriginalUpAxis()))

for node in scene_nodes:
    node_attr = node.GetNodeAttribute()

    if isinstance(node_attr, fbx.FbxNull):  # This is what 'groups' are in 3ds Max/Maya
        # In order to turn a group into a LOD group, the LOD Group
        # needs to be created with all the trimmings
        lod_group_attr = fbx.FbxLODGroup.Create(manager, '')  # type: fbx.FbxLODGroup

        lod_group_attr.WorldSpace.Set(False)
        lod_group_attr.MinMaxDistance.Set(False)
        lod_group_attr.MinDistance.Set(0.0)
        lod_group_attr.MaxDistance.Set(0.0)

        child_num = node.GetChildCount()

        for x in range(0, child_num):
            print(node.GetChild(x).GetName())

            # Add some thresholds!
            # LOD Groups produced from Max/Maya do not create thresholds for all the children.
            # They do not make one for the last LOD - not exactly sure why but i have replicated that here with great success!
            # Just use some random values for testing. Doesn't matter with UE4 at least.
            # It won't matter either with Max/Maya as I will add/remove the LOD Group attribute on export/import
            if x == (child_num-1):
                continue
            elif x == 0:
                threshold = fbx.FbxDistance((x + 1) * 12.0, '')
            else:
                threshold = fbx.FbxDistance(x * 20, '')

            lod_group_attr.AddThreshold(threshold)

            lod_group_attr.SetDisplayLevel(x, 0)  # UseLOD DisplayLevel - Default in Maya :)

            print(lod_group_attr.GetThreshold(x), lod_group_attr.GetDisplayLevel(x))

        node.SetNodeAttribute(lod_group_attr)  # This is VIP!!! Don't forget about this again! xD

        # Export the file. Same process as importing - Create the Exporter, Initialize it, export!
        exporter = fbx.FbxExporter.Create(manager, 'Exporter')

        # The SceneRenamer() is only used for FBX version, makes sure the string doesn't contain characters the various formats/programs don't like
        scene_renamer = fbx.FbxSceneRenamer(scene)
        # manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_MATERIAL, False)
        # manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_TEXTURE, False)
        # manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_SHAPE, True)
        # manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_GLOBAL_SETTINGS, True)

        # I got this string from fbxio.h (which works in 2015) in FBX SDK Reference > Files > File List > fbxsdk > fileio > fbx
        exporter.SetFileExportVersion('FBX201400', scene_renamer.eFBX_TO_FBX)
        exporter.Initialize('test.fbx', -1, manager.GetIOSettings())

        exporter.Export(scene)
        exporter.Destroy()
    elif isinstance(node_attr, fbx.FbxLODGroup):
        # Need to parent the old LOD group children to a new empty 'group' node
        # (A node with NULL properties)
        # Make sure it's destroyed as it's not needed anymore ;)
        # Get the children in the group first
        lod_group_nodes = [node.GetChild(x) for x in range(0, node.GetChildCount())]

        # But 1st - those attributes need to be cleaned up! (for testing purposes)
        # group_props = []  # for seeing all custom properties on all objects
        for group_node in lod_group_nodes:
            print(group_node.GetName())
            # count = 0

            # Because of the C++ nature of SDK (and these bindings), a normal for loop is not possible for collecting properties
            # A collection must be made with a while loop
            properties = []
            group_node_prop = group_node.GetFirstProperty()  # type: fbx.FbxProperty
            while group_node_prop.IsValid():
                # count += 1
                # Only the User-defined Properties are wanted (defined by user and not by SDK)
                # These are Custom Attributes from Maya (and 3ds Max) AND User-defined Properties from 3ds Max (mmm perhaps something to convert to/from Custom Attributes on export/import?)
                if group_node_prop.GetFlag(fbx.FbxPropertyFlags.eUserDefined):
                    properties.append(group_node_prop)
                    # group_props.append(properties)  # for seeing all custom properties on all objects
                group_node_prop = group_node.GetNextProperty(group_node_prop)

            for custom_prop in properties:
                data = custom_prop.GetPropertyDataType()  # type: fbx.FbxDataType

                if data.GetType() == fbx.eFbxString:
                    custom_prop = fbx.FbxPropertyString(custom_prop)

                    # This is not needed when importing into 3ds Max as it is passed to the UV Channel directly (See Channel Info.. Window).
                    # Not sure about Maya but when re-imported it still works without it (when removed after)? - Needs testing with multiple UV channels
                    if custom_prop.GetName() == 'currentUVSet':
                        # Destorying the property while connected seems to fuck up the rest of the properties so be sure to disconnect it first!
                        custom_prop.DisconnectAllSrcObject()
                        custom_prop.Destroy()

                    # This comes from Maya UV set names being injected into the User-Defined Properties in 3ds Max (NOT Custom Attributes) thus creating crap data.
                    # Unless cleaned up/converted on import/export or utilised in a meaningful way, this can be removed.
                    # Further testing needs to be done with this. (Relates to Custom Attributes and User-Defined Properties earlier talk)
                    elif custom_prop.GetName() == 'UDP3DSMAX':
                        custom_prop.DisconnectAllSrcObject()
                        custom_prop.Destroy()

                    else:
                        print("{}\n  type: {}\n\tValue: {}".format(custom_prop.GetName(), data.GetName(), custom_prop.Get()))

                elif data.GetType() == fbx.eFbxInt:
                    custom_prop = fbx.FbxPropertyInteger1(custom_prop)

                    # This comes from 3ds Max as well - Not sure where this comes from xD
                    # Doesn't seem to have any effect though??
                    if custom_prop.GetName() == 'MaxHandle':
                        custom_prop.DisconnectAllSrcObject()
                        custom_prop.Destroy()

                    elif custom_prop.HasMinLimit() and custom_prop.HasMaxLimit():
                        print("{}\n  type: {}\n\tValue: {}\n\tMinLimit: {}\n\tMaxLimit: {}".format(custom_prop.GetName(), data.GetName(), custom_prop.Get(), custom_prop.GetMinLimit(), custom_prop.GetMaxLimit()))
                    else:
                        print("{}\n  type: {}\n\tValue: {}".format(custom_prop.GetName(), data.GetName(), custom_prop.Get()))

                elif data.GetType() == fbx.eFbxBool:
                    custom_prop = fbx.FbxPropertyBool1(custom_prop)
                    print(
                        "{}\n  type: {}\n\tValue: {}".format(custom_prop.GetName(), data.GetName(), custom_prop.Get()))

                elif data.GetType() == fbx.eFbxDouble:  # Number type - Similar to float but instead of 32-bit data type, 64-bit data type.
                    custom_prop = fbx.FbxPropertyFloat1(custom_prop)
                    if custom_prop.HasMinLimit() and custom_prop.HasMaxLimit():
                        print("{}\n  type: {}\n\tValue: {}\n\tMinLimit: {}\n\tMaxLimit: {}".format(custom_prop.GetName(), data.GetName(), custom_prop.Get(), custom_prop.GetMinLimit(), custom_prop.GetMaxLimit()))
                    else:
                        print("\tValue: {}".format(custom_prop.Get()))

                # After All of this, ONLY our Custom Attributes should be left (and NOT any weird 3ds Max stuff xD )
                # Now to finally remove all of them (ONLY FOR TESTING PURPOSES)
                custom_prop.DisconnectAllSrcObject()
                custom_prop.Destroy()

        # Now that we have done what wanted to do, it is time to destroy the LOD Group node (the children are safely somewhere else)
        node.DisconnectAllSrcObject()
        node.Destroy()

        new_group = fbx.FbxNode.Create(manager, 'group')
        for x in range(0, len(lod_group_nodes)):
            child = lod_group_nodes[x]
            new_group.AddChild(child)

        root_node.AddChild(new_group)  # Make sure it's in the scene!

        # Export the file. Same process as importing - Create the Exporter, Initialize it, export!
        exporter = fbx.FbxExporter.Create(manager, 'Exporter')

        # The SceneRenamer() is only used for FBX version, makes sure the string doesn't contain characters the various formats/programs don't like
        scene_renamer = fbx.FbxSceneRenamer(scene)

        # Most of the IO settings are True by default so no need to set any...for now!
        # I got this string from fbxio.h (which works in 2015) in FBX SDK Reference > Files > File List > fbxsdk > fileio > fbx
        exporter.SetFileExportVersion('FBX201400', scene_renamer.eFBX_TO_FBX)
        exporter.Initialize('test_no_lod.fbx', -1, manager.GetIOSettings())

        exporter.Export(scene)
        exporter.Destroy()

    else:
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
