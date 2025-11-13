from pathlib import Path

import fbx
import FbxCommon

from lodbox import fbx_io
from lodbox import scene

file_paths = {'Attributes': "Sphere_Attr.fbx",
              'lodGroup': "Sphere_lodGroup.fbx",
              'lodGroup_Max': "Sphere_lodGroup_Max.FBX",
              'Group_lods': "Sphere_group_lods.fbx",
              'MergeSceneTest01': "MergeSceneTest01.FBX",
              'MergeSceneTest02': "MergeSceneTest02.FBX",
              'MergeSceneTest03': "MergeSceneTest03.FBX",
              'MergeSceneTest_Merged': "MergeSceneTest_Merged.FBX",
              'test_merged_scenes': Path(Path.cwd(), "test_merged_scenes.fbx")
              }  # Hardcoded for now.
# The full path gets injected into the DocumentUrl when exporting. If there is just a filename, then it gets exported into the current working directory.


# FbxCommon contains some helper functions to get rid of some boilerplate
manager: fbx.FbxManager
fbx_scene: fbx.FbxScene
manager, fbx_scene = FbxCommon.InitializeSdkObjects()
global_settings: fbx.FbxGlobalSettings = fbx_scene.GetGlobalSettings()

ImportFBX = fbx_io.import_scene

# FbxCommon.LoadScene(manager, fbx_scene, file_paths['lodGroup_Max'])
# fbx_io.import_scene(manager, fbx_scene, file_paths['lodGroup'])
# ImportFBX(manager, fbx_scene, file_paths['Group_lods'])
ImportFBX(manager, fbx_scene, file_paths['MergeSceneTest01'])
# FbxCommon.LoadScene(manager, fbx_scene, file_paths['MergeSceneTest_Merged'])

root_node: fbx.FbxNode = fbx_scene.GetRootNode()

# 1st method of getting high-level scene nodes
# Using root_node.GetChildCount(True) (returns number of children with recursion)
# to get all scene nodes but returns None for grandchildren and lower
scene_nodes = [root_node.GetChild(i) for i in range(root_node.GetChildCount())]
print(f"Total number of nodes in the scene are: {root_node.GetChildCount(True)}\n"
      f"The root node is: {root_node.GetName()}\n"
      f"Scene Units: {global_settings.GetSystemUnit().GetScaleFactorAsString()}"
      f"\n{global_settings.GetOriginalUpAxis()}: Z-UP")

for node in scene_nodes:
    node_attr: fbx.FbxNodeAttribute = node.GetNodeAttribute()

    # # FbxNull > FbxLODGroup # #
    # Necessary for making LOD Groups OUTSIDE 3ds Max and Maya.
    # It's not SOO bad in Maya, but it is still a black box in terms of scripting.
    if isinstance(node_attr, fbx.FbxNull):
        # # FbxNull nodes are what 'groups' are in Maya.
        # # 3ds Max can create these and can export them but doesn't convert to a native group on import?!
        #
        # # In order to turn a group into a LOD group, the LOD Group first needs to be created with all the trimmings
        # lod_group_attr = fbx.FbxLODGroup.Create(manager, '')  # type: fbx.FbxLODGroup
        #
        # lod_group_attr.WorldSpace.Set(False)
        # lod_group_attr.MinMaxDistance.Set(False)
        # lod_group_attr.MinDistance.Set(0.0)
        # lod_group_attr.MaxDistance.Set(0.0)
        #
        # child_num = node.GetChildCount()
        #
        # for x in range(child_num):
        #     child = node.GetChild(x)
        #     print(child.GetName())
        #
        #     # # CUSTOM ATTRIBUTE REMOVING # #
        #     # Because of a MAXScript error on import
        #     # Custom Attributes should be removed if part of a LOD Group?! (they are still there when the error pops up just not in UI)
        #     # UPDATE: IT WORKS :D (Only now no Custom Attributes :( But see lower implementation for full explanation and possible ideas)
        #     child_properties = []
        #     child_prop = child.GetFirstProperty()  # type: fbx.FbxProperty
        #     while child_prop.IsValid():
        #         if child_prop.GetFlag(fbx.FbxPropertyFlags.eUserDefined):
        #             child_properties.append(child_prop)
        #         child_prop = child.GetNextProperty(child_prop)
        #     for prop in child_properties:
        #         prop.DisconnectAllSrcObject()
        #         prop.Destroy()
        #     # # END OF CUSTOM ATTRIBUTE REMOVING # #
        #
        #     # Add some thresholds!
        #     # LOD Groups produced from Max/Maya do not create thresholds for all the children.
        #     # They do not make one for the last LOD - not exactly sure why, but I have replicated that here with great success!
        #     # Just use some random values for testing. Doesn't matter with UE4 at least.
        #     # It won't matter either with Max/Maya as I will add/remove the LOD Group attribute on export/import
        #     if x == (child_num - 1):
        #         continue
        #     elif x == 0:
        #         threshold = fbx.FbxDistance((x + 1) * 12.0, '')
        #     else:
        #         threshold = fbx.FbxDistance(x * 20, '')
        #
        #     lod_group_attr.AddThreshold(threshold)
        #
        #     lod_group_attr.SetDisplayLevel(x, 0)  # UseLOD DisplayLevel - Default in Maya :)
        #
        #     print(lod_group_attr.GetThreshold(x), lod_group_attr.GetDisplayLevel(x))
        #
        # node.SetNodeAttribute(lod_group_attr)  # This is VIP!!! Don't forget about this again! xD
        scene.create_lod_group_attribute(manager, node)

        fbx_io.export_scene_fbx(manager=manager, scene=fbx_scene, fbx_version=fbx_io.FBX_VERSION['2014'], file_path=Path(Path.cwd(), "test_lod_group.fbx"), file_format=fbx_io.LodBoxFbxFormat.BINARY)

    # # FbxLODGroup > FbxNull # #
    # "Extracting" normal meshes out of LOD Groups so don't have to deal with that in 3ds Max/Maya (at least 1st steps)
    elif isinstance(node_attr, fbx.FbxLODGroup):
        # # Need to parent the old LOD group children to a new empty 'group' node
        # # (A node with NULL properties)
        # # Make sure it's destroyed as it's not needed anymore ;)
        # # Get the children in the group first
        # lod_group_nodes = lodbox.scene.get_children(node)
        #
        # # But 1st - those attributes need to be cleaned up! (for testing purposes)
        # # group_props = []  # for seeing all custom properties on all objects
        # for group_node in lod_group_nodes:
        #     print(group_node.GetName())
        #     # count = 0
        #
        #     # Because of the C++ nature of SDK (and these bindings), a normal for loop is not possible for collecting properties
        #     # A collection must be made with a while loop
        #     properties = []
        #     group_node_prop = group_node.GetFirstProperty()  # type: fbx.FbxProperty
        #     while group_node_prop.IsValid():
        #         # count += 1
        #         # Only the User-defined Properties are wanted (defined by user and not by SDK)
        #         # These are Custom Attributes from Maya (and 3ds Max)
        #         # AND User-defined Properties from 3ds Max (mmm perhaps something to convert to/from Custom Attributes on export/import?)
        #         if group_node_prop.GetFlag(fbx.FbxPropertyFlags.eUserDefined):
        #             properties.append(group_node_prop)
        #             # group_props.append(properties)  # for seeing all custom properties on all objects
        #         group_node_prop = group_node.GetNextProperty(group_node_prop)
        #
        #     for custom_prop in properties:
        #         data = custom_prop.GetPropertyDataType()  # type: fbx.FbxDataType
        #
        #         if data.GetType() == fbx.eFbxString:
        #             custom_prop = fbx.FbxPropertyString(custom_prop)
        #
        #             # This is not needed when importing into 3ds Max as it is passed to the UV Channel directly (See "Channel Info.." Window).
        #             # Not sure about Maya but when re-imported it still works without it (when removed after)? - Needs testing with multiple UV channels
        #             if custom_prop.GetName() == 'currentUVSet':
        #                 # Destroying the property while connected seems to fuck up the rest of the properties so be sure to disconnect it first!
        #                 custom_prop.DisconnectAllSrcObject()
        #                 custom_prop.Destroy()
        #
        #             # This comes from Maya UV set names being injected into the User-Defined Properties in 3ds Max (NOT Custom Attributes) thus creating crap data.
        #             # Unless cleaned up/converted on import/export or utilised in a meaningful way, this can be removed.
        #             # Further testing needs to be done with this. (Relates to Custom Attributes and User-Defined Properties earlier talk)
        #             elif custom_prop.GetName() == 'UDP3DSMAX':
        #                 custom_prop.DisconnectAllSrcObject()
        #                 custom_prop.Destroy()
        #
        #             else:
        #                 print("{}\n  type: {}\n\tValue: {}".format(custom_prop.GetName(), data.GetName(), custom_prop.Get()))
        #
        #         elif data.GetType() == fbx.eFbxInt:
        #             custom_prop = fbx.FbxPropertyInteger1(custom_prop)
        #
        #             # This comes from 3ds Max as well - Not sure where this comes from xD
        #             # Doesn't seem to have any effect though??
        #             if custom_prop.GetName() == 'MaxHandle':
        #                 custom_prop.DisconnectAllSrcObject()
        #                 custom_prop.Destroy()
        #
        #             elif custom_prop.HasMinLimit() and custom_prop.HasMaxLimit():
        #                 print("{}\n  type: {}\n\tValue: {}\n\tMinLimit: {}\n\tMaxLimit: {}".format(custom_prop.GetName(), data.GetName(),
        #                                                                                            custom_prop.Get(), custom_prop.GetMinLimit(),
        #                                                                                            custom_prop.GetMaxLimit()))
        #             else:
        #                 print("{}\n  type: {}\n\tValue: {}".format(custom_prop.GetName(), data.GetName(), custom_prop.Get()))
        #
        #         elif data.GetType() == fbx.eFbxBool:
        #             custom_prop = fbx.FbxPropertyBool1(custom_prop)
        #             print("{}\n  type: {}\n\tValue: {}".format(custom_prop.GetName(), data.GetName(), custom_prop.Get()))
        #
        #         elif data.GetType() == fbx.eFbxDouble:  # Number type - Similar to float but instead of 32-bit data type, 64-bit data type.
        #             custom_prop = fbx.FbxPropertyDouble1(custom_prop)
        #             if custom_prop.HasMinLimit() and custom_prop.HasMaxLimit():
        #                 print("{}\n  type: {}\n\tValue: {}\n\tMinLimit: {}\n\tMaxLimit: {}".format(custom_prop.GetName(), data.GetName(),
        #                                                                                            custom_prop.Get(), custom_prop.GetMinLimit(),
        #                                                                                            custom_prop.GetMaxLimit()))
        #             else:
        #                 print("\tValue: {}".format(custom_prop.Get()))
        #
        #         # After All of this, ONLY our Custom Attributes should be left (and NOT any weird 3ds Max stuff xD )
        #         # Now to finally remove all of them (ONLY FOR TESTING PURPOSES)
        #         custom_prop.DisconnectAllSrcObject()
        #         custom_prop.Destroy()
        #
        # # Now that we have done what wanted to do, it is time to destroy the LOD Group node (the children are safely somewhere else)
        # node.DisconnectAllSrcObject()
        # node.Destroy()
        #
        # new_group = fbx.FbxNode.Create(manager, 'group')
        # for lod_grp_node in lod_group_nodes:
        #     new_group.AddChild(lod_grp_node)
        #
        # root_node.AddChild(new_group)  # Make sure it's in the scene!

        node = scene.convert_node_to_null(manager, node)
        node_attr: fbx.FbxNodeAttribute = node.GetNodeAttribute()
        # TODO: Now that lod group attr > null is done, extracting meshes as individual files could be done
        #  (maybe with selection somehow say - only want to change LOD3 and then recombine)
        # lodbox.fbx_io.export_scene_fbx(manager, scene, version=lodbox.fbx_io.FBX_VERSION['2014'], filename="test_no_lod_group", file_format=lodbox.fbx_io.FBX_FORMAT['Binary'])

        # # EXTRACTING MESHES
        lod_group_children = scene.get_children(node)
        if lod_group_children:

            export_scene: fbx.FbxScene = fbx.FbxScene.Create(manager, "ExportScene")
            export_scene_root: fbx.FbxNode = export_scene.GetRootNode()

            child: fbx.FbxNode
            for child in lod_group_children:
                # TODO: MAKE A NEW TEMP SCENE FOR EXPORTING EACH THING (OR REUSE EXISTING ONE)
                #  AS USING SCENE VARIABLE NOW JUST EXPORTS THE SCENE ALL THE TIME :D
                # simple flow:
                #   make a (temp) scene (or maybe for export...)
                #   get child node and attach to new scene root
                #   disconnect from old node(s)

                lod_scene: fbx.FbxScene = fbx.FbxScene.Create(manager, f"{child.GetName()}_scene")
                lod_scene_root_node: fbx.FbxNode = lod_scene.GetRootNode()
                print(child.GetName(),
                      child.GetDstObject(0),
                      lod_scene.GetName(),
                      lod_scene_root_node.GetName()
                      )

                # The parent node (LODGroup) is a destination object and there could be others too hence the DisconnectAllDstObject() method instead of doing individually.
                child.DisconnectAllDstObject()

                # going through the merge_scenes()/move_nodes() function
                # but only want to add ONE node it is not the same...

                print(f"export root count: {export_scene_root.GetSrcObjectCount()}")
                print(f"scene root count: {root_node.GetSrcObjectCount()}")
                export_scene_root.AddChild(child)
                print(f"export root count: {export_scene_root.GetSrcObjectCount()}")
                print(f"scene root count: {root_node.GetSrcObjectCount()}")
                root_node.DisconnectSrcObject(child)

                for index in range(fbx_scene.GetSrcObjectCount()):
                    fbx_obj: fbx.FbxObject = fbx_scene.GetSrcObject(index)

                    # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
                    # The equality check is split as the root node is an instance of fbx.FbxNode type but other objects such as fbx.FbxGlobalSettings
                    # are subclasses of the fbx.FbxNode type but NOT instances. A little weird but this works!
                    # The == equality check could be used as fallback for isinstance() if necessary
                    if isinstance(fbx_obj, type(root_node)):
                        continue
                    elif issubclass(type(fbx_obj), (fbx.FbxGlobalSettings, fbx.FbxAnimEvaluator, fbx.FbxAnimStack, fbx.FbxAnimLayer)):
                        continue
                    else:
                        # print(fbx_obj.GetName(), type(fbx_obj))
                        fbx_obj.ConnectDstObject(export_scene)

                print(f"Scene Source Object Count: {export_scene.GetSrcObjectCount()}\n")

                fbx_io.export_scene_fbx(manager, export_scene, fbx_version=fbx_io.FBX_VERSION[2014], file_path=child.GetName(), file_format=fbx_io.LodBoxFbxFormat.ASCII)

                # export_scene.DisconnectSrcObject()

            scene.destroy_fbx_object(export_scene)

        else:
            raise IndexError

        manager.Destroy()

    # # Merging Scenes Test # #
    # Starting with MergeTestScene01
    elif node.GetName() == "Sphere001":
        reference_scene = scene.merge_scenes(manager, fbx_scene, (file_paths['MergeSceneTest02'], file_paths['MergeSceneTest03']))

        # # Create a new scene to hold the already imported scene (probably can just the original normally but this is useful for testing ;) )
        # reference_scene = fbx.FbxScene.Create(manager, "ReferenceScene")
        # # Start moving stuff to new scene (already have the scene nodes in list from above)
        # ref_scene_root = reference_scene.GetRootNode()  # type: fbx.FbxNode
        #
        # # Since the default Axis System is Y-Up and because these are brand-new settings (its made with a scene along with FbxAnimEvaluator and a Root Node),
        # # the axis needs to be set to the same as the original imported scene!
        # orig_axis_sys = fbx.FbxAxisSystem(global_settings.GetAxisSystem())
        # orig_axis_sys.ConvertScene(reference_scene)
        #
        # # Because this is a test, the original scene_nodes list is used, otherwise this would be the
        # # MergeTestScene01 nodes.
        # for x in range(len(scene_nodes)):
        #     child = scene_nodes[x]
        #     ref_scene_root.AddChild(child)
        # # Although the original Sphere001 is attached to new Reference Scene root node, it is still connected to the old one
        # # so the connections need to be removed. And because there could be lots of children, it is better to disconnect the root node from the children.
        # root_node.DisconnectAllSrcObject()
        # print(fbx_obj.GetName(),
        #       type(fbx_obj), issubclass(type(fbx_obj), (fbx.FbxGlobalSettings, fbx.FbxAnimEvaluator, fbx.FbxAnimStack, fbx.FbxAnimLayer)),
        #       issubclass(type(fbx_obj), type(source_scene_root)), isinstance(fbx_obj, type(source_scene_root))
        #       )
        #
        # # Because the scene Object also has connections to other types of FBX objects, they need to be moved too.
        # # (I'm guessing) Also since there is only a single mesh in the FBX, the scene has connections to that too.
        # for x in range(scene.GetSrcObjectCount()):
        #     fbx_obj = scene.GetSrcObject(x)  # type: fbx.FbxObject
        #     print(type(fbx_obj), fbx_obj.ClassId)
        #     # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
        #     # Can use type(fbx_obj), fbx_obj.GetClassId() or fbx_obj.ClassId to type check
        #     if fbx_obj == root_node or \
        #             fbx_obj.ClassId == fbx.FbxGlobalSettings.ClassId or \
        #             type(fbx_obj) == fbx.FbxAnimEvaluator or \
        #             fbx_obj.ClassId == fbx.FbxAnimStack.ClassId or \
        #             fbx_obj.ClassId == fbx.FbxAnimLayer.ClassId:
        #         continue
        #     else:
        #         fbx_obj.ConnectDstObject(reference_scene)
        #
        # # Now the scene can be disconnected as everything has been moved!
        # scene.DisconnectAllSrcObject()
        #
        # print("merged stuff starts from here")
        # # Now that the first scene has been moved from the original and disconnected, time to start
        # # merging MergeTestScene02.
        # # It seems a new scene HAS to be created for each scene (perhaps revisit this at some point?)
        # # So start off with creating/loading scene to merge in
        # # EDIT: NOPE - I WAS JUST ALWAYS EXPORTING THE ORIGINAL SCENE - The original scene can be used! :D
        # FbxCommon.LoadScene(manager, scene, file_paths['MergeSceneTest02'])
        # scene_nodes = [root_node.GetChild(i) for i in range(root_node.GetChildCount())]
        #
        # # Repeat adding the new scene nodes to the reference scene and disconnecting to old one
        # for x in range(len(scene_nodes)):
        #     child = scene_nodes[x]
        #     ref_scene_root.AddChild(child)
        # root_node.DisconnectAllSrcObject()
        #
        # # # Move other types of scene objects again
        # for x in range(scene.GetSrcObjectCount()):
        #     fbx_obj = scene.GetSrcObject(x)  # type: fbx.FbxObject
        #     # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
        #     if fbx_obj == root_node or fbx_obj.GetClassId() == fbx.FbxGlobalSettings.ClassId or type(
        #             fbx_obj) == fbx.FbxAnimEvaluator or fbx_obj.ClassId == fbx.FbxAnimStack.ClassId or fbx_obj.ClassId == fbx.FbxAnimLayer.ClassId:
        #         continue
        #     else:
        #         fbx_obj.ConnectDstObject(reference_scene)
        # scene.DisconnectAllSrcObject()  # DON'T FORGET TO DISCONNECT THE ORIGINAL SCENE FROM THE MOVED OBJECTS!
        #
        # # ## 2nd MERGE STUFF
        # FbxCommon.LoadScene(manager, scene, file_paths['MergeSceneTest03'])
        # scene_nodes = [root_node.GetChild(i) for i in range(root_node.GetChildCount())]
        # for x in range(len(scene_nodes)):
        #     child = scene_nodes[x]
        #     ref_scene_root.AddChild(child)
        # root_node.DisconnectAllSrcObject()
        #
        # # Move other types of scene objects again
        # for x in range(scene.GetSrcObjectCount()):
        #     fbx_obj = scene.GetSrcObject(x)  # type: fbx.FbxObject
        #     # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
        #     if fbx_obj == root_node or \
        #             fbx_obj.GetClassId() == fbx.FbxGlobalSettings.ClassId or \
        #             type(fbx_obj) == fbx.FbxAnimEvaluator or \
        #             fbx_obj.ClassId == fbx.FbxAnimStack.ClassId or \
        #             fbx_obj.ClassId == fbx.FbxAnimLayer.ClassId:
        #         continue
        #     else:
        #         print(fbx_obj.GetClassId().GetName())
        #         fbx_obj.ConnectDstObject(reference_scene)
        # scene.DisconnectAllSrcObject()  # DON'T FORGET TO DISCONNECT THE ORIGINAL SCENE FROM THE MOVED OBJECTS!

        # ## FBX EXPORT ##
        # Okay, so it works! BUT it seems to be almost double the file-size than if I had exported them from 3ds Max (or Maya)?!
        # EDIT: I found the cause :D when comparing the files as ASCII, the FBX version has Tangents and Binormals so that is the extra data :)
        # Normally, I don't export these so hence my confusion! I wonder if they can be excluded....?
        fbx_io.export_scene_fbx(manager, reference_scene, fbx_io.FBX_VERSION[2014], file_paths['test_merged_scenes'], fbx_io.LodBoxFbxFormat.ASCII)
        for x in range(reference_scene.GetSrcObjectCount()):
            print(reference_scene.GetSrcObject(x), reference_scene.GetSrcObject(x).GetName())

        manager.Destroy()

    else:
        print(node.GetName(), type(node))
