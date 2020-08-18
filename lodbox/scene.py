from __future__ import print_function
import fbx
import FbxCommon


# TODO: FIGURE OUT MERGING SCENES IN LESS "TESTY" WAY
# Merge flow:
# INPUT(S) - List of files or perhaps existing scene?
# 1st time:
#   Load file, get scene, get root, collect nodes into a list, move to merged scene
# Subsequent times:
#   Load new file with old scene, collect nodes again into a list, move to merged scene
class LodBoxFbx(object):
    def __init__(self, manager, scene):
        self.manager = manager
        self.scene = scene

        self.scene_root = self.scene.GetRootNode()
        self.scene_nodes = [self.scene_root.GetChild(i) for i in range(self.scene_root.GetChildCount())]

    def __repr__(self):
        return self.__class__.__name__

    def disconnect(self):
        pass


def merge(manager, *args):
    # Create a new scene to hold the soon-to-be merged scene which will be used for exporting (or other things.)
    # For merging, a new scene needs to be made so each new file loaded will not overwrite the old scene.
    merged_scene = fbx.FbxScene.Create(manager, "MergedScene")
    merged_scene_root = merged_scene.GetRootNode()  # type: fbx.FbxNode

    first_scene = args[0]  # type: fbx.FbxScene
    first_scene_root = first_scene.GetRootNode()  # type: fbx.FbxNode

    # Since the default Axis System is Y-Up and because these are brand new settings (its made with a scene along with FbxAnimEvaluator and a Root Node),
    # the axis needs to be set to the same as the original imported scene!
    orig_axis_sys = fbx.FbxAxisSystem(first_scene.GetGlobalSettings().GetAxisSystem())
    orig_axis_sys.ConvertScene(merged_scene)

    for x in range(len(first_scene)):
        child = first_scene[x]
        merged_scene_root.AddChild(child)
    # Although the original nodes are attached to new Merged Scene root node, they are still connected to the old one and
    # so the connections need to be removed. Because there could be lots of children, its better to disconnect the root node from the children.
    first_scene_root.DisconnectAllSrcObject()

    # Because the scene Object also has connections to other types of FBX objects, they need to be moved too.
    # (I'm guessing) Also since there could be only a single mesh in the FBX, the scene has connections to that too.
    for x in range(first_scene.GetSrcObjectCount()):
        fbx_obj = first_scene.GetSrcObject(x)  # type: fbx.FbxObject
        print(type(fbx_obj))
        # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
        if isinstance(fbx_obj, (first_scene_root, fbx.FbxGlobalSettings, fbx.FbxAnimEvaluator, fbx.FbxAnimStack, fbx.FbxAnimLayer)):
            continue
        else:
            fbx_obj.ConnectDstObject(merged_scene)

    # Now the scene can be disconnected as everything has been moved!
    first_scene.DisconnectAllSrcObject()

    # 2ND MERGE STUFF
    FbxCommon.LoadScene(manager, first_scene, args[1])
    scene_nodes = [first_scene_root.GetChild(i) for i in range(first_scene_root.GetChildCount())]

    # Repeat adding the new scene nodes to the reference scene and disconnecting to old one
    for x in range(len(scene_nodes)):
        child = scene_nodes[x]
        merged_scene_root.AddChild(child)
    first_scene_root.DisconnectAllSrcObject()

    # # Move other types of scene objects again
    for x in range(first_scene.GetSrcObjectCount()):
        fbx_obj = first_scene.GetSrcObject(x)  # type: fbx.FbxObject
        # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
        if isinstance(fbx_obj, (first_scene_root, fbx.FbxGlobalSettings, fbx.FbxAnimEvaluator, fbx.FbxAnimStack, fbx.FbxAnimLayer)):
            continue
        else:
            fbx_obj.ConnectDstObject(merged_scene)
    first_scene.DisconnectAllSrcObject()  # DON'T FORGET TO DISCONNECT THE ORIGINAL SCENE FROM THE MOVED OBJECTS!


def move_nodes():
    pass


# TODO: FINISH THIS FUNCTION : Maybe have the distances?
def create_lod_group(manager, node, is_world_space=False, set_min_max=False, min_distance=-100.0, max_distance=100.0):
    """
    Creates a LOD Group by adding the Fbx.FbxLODGroup node attribute. A node should have children!

    :type manager: fbx.FbxManager
    :type node: fbx.FbxNull
    :type is_world_space: bool
    :type set_min_max: bool
    :type min_distance: float
    :type max_distance: float
    """
    # # FbxNull > FbxLODGroup # #
    # Necessary for making LOD Groups OUTSIDE of DCC program.
    # It's not SOO bad in Maya but it is still a black box in terms of scripting.
    # FbxNull nodes are what 'groups' are in Maya.
    # 3ds Max can create these and can export them but doesn't convert to a native group on import?!

    lod_group_attr = fbx.FbxLODGroup.Create(manager, '')  # type: fbx.FbxLODGroup
    lod_group_attr.WorldSpace.Set(is_world_space)
    lod_group_attr.MinMaxDistance.Set(set_min_max)
    if set_min_max:
        lod_group_attr.MinDistance.Set(min_distance)
        lod_group_attr.MaxDistance.Set(max_distance)

    for index in range(node.GetChildCount()):
        # LOD Groups produced from Max/Maya do not create thresholds for all the children.
        # They do not make one for the last LOD - not exactly sure why but i have replicated that here with great success!
        # Just use some random values for testing. Doesn't matter with UE4 at least.
        # It won't matter either with Max/Maya as I will add/remove the LOD Group attribute on export/import
        if index == (node.GetChildCount() - 1):
            continue
        elif index == 0:
            threshold = fbx.FbxDistance((index + 1) * 12.0, '')
        else:
            threshold = fbx.FbxDistance(index * 20, '')

        lod_group_attr.AddThreshold(threshold)
        lod_group_attr.SetDisplayLevel(index, 0)  # Use LOD DisplayLevel - Default in Maya :) It seems that this

    node.SetNodeAttribute(lod_group_attr)  # This is VIP!!! Don't forget about this again! xD

    return False
