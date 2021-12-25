from typing import Tuple

import fbx

import fbx_io


# Merge flow:
# INPUT(S) - List of files or perhaps existing scene?
# 1st time:
#   Load file, get scene, get root, collect nodes into a list, move to merged scene
# Subsequent times:
#   Load new file with old scene, collect nodes again into a list, move to merged scene
class LodBoxFbx(object):
    def __init__(self, manager: fbx.FbxManager, scene: fbx.FbxScene):
        self.manager = manager
        self.scene = scene

        self.scene_root = self.scene.GetRootNode()
        self.scene_nodes = get_children(self.scene_root)

    def __repr__(self):
        return self.__class__.__name__

    def disconnect(self):
        pass


def get_children(node: fbx.FbxNode) -> list:
    """
    Gets the children of the node (Not recursive though)

    """
    return [node.GetChild(i) for i in range(node.GetChildCount())]


def destroy_fbx_object(node: fbx.FbxNode):
    """
    Disconnects and destroys the node
    """
    if node.DisconnectAllSrcObject():
        node.Destroy()
    else:
        print(F"Couldn't destroy {node.GetName()}")


def merge_scenes(manager: fbx.FbxManager, first_scene: fbx.FbxScene, scenes_to_merge: Tuple[str, ...]) -> fbx.FbxScene:
    """
    Merges first scene with the other scenes.

    """
    # Create a new scene to hold the soon-to-be merged scene which will be used for exporting (or other things.)
    # For merging, a new scene needs to be made so each new file loaded will not overwrite the old scene.
    merged_scene = fbx.FbxScene.Create(manager, "MergedScene")

    # Since the default Axis System is Y-Up and because these are brand-new settings (its made with a scene along with FbxAnimEvaluator and a Root Node),
    # the axis needs to be set to the same as the original imported scene!
    orig_axis_sys = fbx.FbxAxisSystem(first_scene.GetGlobalSettings().GetAxisSystem())
    orig_axis_sys.ConvertScene(merged_scene)

    # Move the 1st scene nodes to the new destination scene ("MergedScene") without importing the scene as that would be done outside this function.
    move_nodes(first_scene, merged_scene)

    # The same variable and scene can be used instead of creating new scenes all the time!
    for scene in scenes_to_merge:
        fbx_io.import_scene(manager, first_scene, scene)
        move_nodes(first_scene, merged_scene)

    return merged_scene


def move_nodes(source_scene: fbx.FbxScene, dest_scene: fbx.FbxScene):
    """
    Moves scene nodes from the source scene to the destination scene.

    """

    source_scene_root = source_scene.GetRootNode()  # type: fbx.FbxNode
    dest_scene_root = dest_scene.GetRootNode()  # type: fbx.FbxNode

    for node in get_children(source_scene_root):
        dest_scene_root.AddChild(node)

    # Although the original nodes are attached to the destination Scene root node, they are still connected to the old one
    # so the connections must be removed. Since there could be lots of children, its better to disconnect the root node from the children.
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


def create_lod_group_attribute(manager: fbx.FbxManager, node: fbx.FbxNull,
                               is_world_space: bool = False, set_min_max: bool = False,
                               min_distance: float = -100.0, max_distance: float = 100.0) -> bool:
    """
    Creates a Fbx.FbxLODGroup node attribute and sets that on the node. A node should have children!

    """
    # # FbxNull > FbxLODGroup # #
    # Necessary for making LOD Groups OUTSIDE of the DCC program.
    # It's not SOO bad in Maya, but it is still a black box in terms of scripting.
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


def convert_node_to_null(manager: fbx.FbxManager, node: fbx.FbxNode) -> fbx.FbxNode:
    """
    Converts a node with the LODGroup attribute to a node with the Null attribute (destroys the old one in the process).
    Also removes any custom attributes too (for now).

    """

    # Need to parent the old LOD group children to a new empty 'group' node
    # (A node with NULL properties)
    lod_group_nodes = get_children(node)

    prev_node_name = node.GetName()
    scene_root_node = node.GetScene().GetRootNode()  # Used for later so that the new group node can be parented to it

    # Now that we have done what wanted to do, it is time to destroy the LOD Group node (the children are safely somewhere else)
    destroy_fbx_object(node)
    del node

    new_group_node = fbx.FbxNode.Create(manager, prev_node_name)

    null_prop = fbx.FbxNull.Create(manager, "")  # Make sure to explicitly create
    new_group_node.SetNodeAttribute(null_prop)  # and set a Fbx.FbxNull property!!

    for lod_grp_node in lod_group_nodes:
        remove_custom_attributes(lod_grp_node)
        new_group_node.AddChild(lod_grp_node)

    scene_root_node.AddChild(new_group_node)  # Make sure it's in the scene!
    return new_group_node


def pprint_custom_property_data(property_data: fbx.FbxDataType):

    print(F"\tName: {property_data.GetName()}\n"
          F"\tValue: {property_data.Get()}")
    if property_data.HasMinLimit() and property_data.HasMaxLimit():
        print(F"\tMinLimit: {property_data.GetMinLimit()}\n"
              F"\tMaxLimit: {property_data.GetMaxLimit()}")


def remove_custom_attributes(node: fbx.FbxNode):

    # TODO: Iterator for node properties?
    # Because of the C++ nature of SDK (and these bindings), a normal for loop is not possible for collecting properties
    # A collection must be made with a while loop
    node_properties = []
    node_prop = node.GetFirstProperty()  # type: fbx.FbxProperty
    while node_prop.IsValid():
        # Only the User-defined Properties are wanted (defined by user and not by SDK)
        # These are Custom Attributes from Maya (and 3ds Max)
        # AND User-defined Properties from 3ds Max (mmm perhaps something to convert to/from Custom Attributes on export/import?)
        if node_prop.GetFlag(fbx.FbxPropertyFlags.eUserDefined):
            node_properties.append(node_prop)

        node_prop = node.GetNextProperty(node_prop)

    for custom_property in node_properties:
        data = custom_property.GetPropertyDataType()  # type: fbx.FbxDataType

        # Can also do data.GetType() == fbx.eFbxString
        if data.Is(fbx.eFbxString):
            custom_property = fbx.FbxPropertyString(custom_property)

            # This is not needed when importing into 3ds Max as it is passed to the UV Channel directly (See Channel Info.. Window).
            # Not sure about Maya but when re-imported it still works without it (when removed after)? - Needs testing with multiple UV channels
            if custom_property.GetName() == 'currentUVSet':
                # Destroying the property while connected seems to fuck up the rest of the properties so be sure to disconnect it first!
                destroy_fbx_object(custom_property)

            # This comes from Maya UV set names being injected into the User-Defined Properties in 3ds Max (NOT Custom Attributes) thus creating crap data.
            # Unless cleaned up/converted on import/export or utilised in a meaningful way, this can be removed.
            # Further testing needs to be done with this. (Relates to Custom Attributes and User-Defined Properties earlier talk)
            elif custom_property.GetName() == 'UDP3DSMAX':
                destroy_fbx_object(custom_property)

            else:
                print(data.GetName())
                pprint_custom_property_data(custom_property)

        elif data.Is(fbx.eFbxInt):
            custom_property = fbx.FbxPropertyInteger1(custom_property)

            # This comes from 3ds Max as well - Not sure where this comes from xD
            # Doesn't seem to have any effect though??
            if custom_property.GetName() == 'MaxHandle':
                destroy_fbx_object(custom_property)

            print(data.GetName())
            pprint_custom_property_data(custom_property)

        elif data.Is(fbx.eFbxBool):
            custom_property = fbx.FbxPropertyBool1(custom_property)
            print(data.GetName())
            pprint_custom_property_data(custom_property)

        elif data.Is(fbx.eFbxDouble):  # Number type - Similar to float but instead of 32-bit data type, 64-bit data type.
            custom_property = fbx.FbxPropertyDouble1(custom_property)
            print(data.GetName())
            pprint_custom_property_data(custom_property)

        # After All of this, ONLY our Custom Attributes should be left (and NOT any weird 3ds Max stuff xD )
        destroy_fbx_object(custom_property)
