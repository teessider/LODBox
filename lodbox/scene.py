from __future__ import print_function, absolute_import

import fbx

import fbx_io


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
        self.scene_nodes = get_children(self.scene_root)

    def __repr__(self):
        return self.__class__.__name__

    def disconnect(self):
        pass


def get_children(node):
    """
    Gets the children of the node (Not recursive though)

    :type node: fbx.FbxNode
    :rtype: list
    """
    return [node.GetChild(i) for i in range(node.GetChildCount())]


# TODO: Finish docstring!
def merge(manager, first_scene, files):
    """

    :type manager: fbx.FbxManager
    :type first_scene: fbx.FbxScene
    :type files: tuple[str]
    :rtype merged_scene: fbx.FbxScene
    """
    # Create a new scene to hold the soon-to-be merged scene which will be used for exporting (or other things.)
    # For merging, a new scene needs to be made so each new file loaded will not overwrite the old scene.
    merged_scene = fbx.FbxScene.Create(manager, "MergedScene")
    merged_scene_root = merged_scene.GetRootNode()  # type: fbx.FbxNode

    first_scene_root = first_scene.GetRootNode()  # type: fbx.FbxNode
    scene_nodes = get_children(first_scene_root)

    # Since the default Axis System is Y-Up and because these are brand new settings (its made with a scene along with FbxAnimEvaluator and a Root Node),
    # the axis needs to be set to the same as the original imported scene!
    orig_axis_sys = fbx.FbxAxisSystem(first_scene.GetGlobalSettings().GetAxisSystem())
    orig_axis_sys.ConvertScene(merged_scene)

    # Move the 1st scene nodes to the new destination scene ("MergedScene") without importing the scene as that would be done outside this function.
    move_nodes(first_scene, first_scene_root, scene_nodes, merged_scene, merged_scene_root)

    # The same variable and scene can be used instead of creating new scenes all the time!
    for scene in files:
        fbx_io.import_scene(manager, first_scene, scene)
        scene_nodes = get_children(first_scene_root)
        move_nodes(first_scene, first_scene_root, scene_nodes, merged_scene, merged_scene_root)

    return merged_scene


# TODO: Finish docstring!
def move_nodes(source_scene, source_scene_root, source_scene_nodes, dest_scene, dest_scene_root):
    """

    :type source_scene: fbx.FbxScene
    :type source_scene_root: fbx.FbxNode
    :type source_scene_nodes: list
    :type dest_scene: fbx.FbxScene
    :type dest_scene_root: fbx.FbxNode
    """

    for node in source_scene_nodes:
        dest_scene_root.AddChild(node)

    # Although the original nodes are attached to the destination Scene root node, they are still connected to the old one and
    # so the connections must to be removed. Since there could be lots of children, its better to disconnect the root node from the children.
    source_scene_root.DisconnectAllSrcObject()

    # Because the Scene Object also has connections to other types of FBX objects, they need to be moved too.
    # (I'm guessing) Also since there could be only a single mesh in the FBX, the scene has connections to that too.
    for index in range(source_scene.GetSrcObjectCount()):
        fbx_obj = source_scene.GetSrcObject(index)  # type: fbx.FbxObject

        # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
        # The equality check is split as the root node is an instance of fbx.FbxNode type but other objects such as fbx.FbxGlobalSettings
        # are subclasses of the fbx.FbxNode type but NOT instances. A little weird but this works!
        # The == equality check could be used as fallback for isinstance() if necessary
        if isinstance(fbx_obj, type(source_scene_root)):
            continue
        elif issubclass(type(fbx_obj), (fbx.FbxGlobalSettings, fbx.FbxAnimEvaluator, fbx.FbxAnimStack, fbx.FbxAnimLayer)):
            continue
        else:
            fbx_obj.ConnectDstObject(dest_scene)

    # Now the scene can be disconnected as everything has been moved!  (DO NOT FORGET THIS STEP)
    return source_scene.DisconnectAllSrcObject()


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
        lod_group_attr.SetDisplayLevel(index, 0)  # Use LOD DisplayLevel - Default in Maya :)

    node.SetNodeAttribute(lod_group_attr)  # This is VIP!!! Don't forget about this again! xD

    return False
