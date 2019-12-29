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
    def __init__(self):
        self.manager = fbx.FbxManager.Create()
        self.scene = fbx.FbxScene.Create(self.manager, "")

        self.scene_root = self.scene.GetRootNode()
        self.scene_nodes = [self.scene_root.GetChild(i) for i in range(self.scene_root.GetChildCount())]

    def __repr__(self):
        return self.__class__.__name__

    def disconnect(self):
        pass

    def merge(self, scenes):
        # Create a new scene to hold the soon-to-be merged scene which will be used for exporting (or other things.)
        # For merging, a new scene needs to be made so each new file loaded will not overwrite the old scene.
        merged_scene = fbx.FbxScene.Create(self.manager, "MergedScene")
        merged_scene_root = merged_scene.GetRootNode()  # type: fbx.FbxNode

        first_scene = scenes[0]  # type: fbx.FbxScene
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
            # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
            if fbx_obj == first_scene_root or fbx_obj.GetClassId() == fbx.FbxGlobalSettings.ClassId or type(fbx_obj) == fbx.FbxAnimEvaluator or fbx_obj.ClassId == fbx.FbxAnimStack.ClassId or fbx_obj.ClassId == fbx.FbxAnimLayer.ClassId:
                continue
            else:
                fbx_obj.ConnectDstObject(merged_scene)

        # Now the scene can be disconnected as everything has been moved!
        first_scene.DisconnectAllSrcObject()

        # 2ND MERGE STUFF
        FbxCommon.LoadScene(self.manager, first_scene, scenes[1])
        scene_nodes = [first_scene_root.GetChild(i) for i in range(0, first_scene_root.GetChildCount())]

        # Repeat adding the new scene nodes to the reference scene and disconnecting to old one
        for x in range(len(scene_nodes)):
            child = scene_nodes[x]
            merged_scene_root.AddChild(child)
        first_scene_root.DisconnectAllSrcObject()

        # # Move other types of scene objects again
        for x in range(first_scene.GetSrcObjectCount()):
            fbx_obj = first_scene.GetSrcObject(x)  # type: fbx.FbxObject
            # Don't want to move the root node, the global settings or the Animation Evaluator (at this point)
            if fbx_obj == first_scene_root or fbx_obj.GetClassId() == fbx.FbxGlobalSettings.ClassId or type(fbx_obj) == fbx.FbxAnimEvaluator or fbx_obj.ClassId == fbx.FbxAnimStack.ClassId or fbx_obj.ClassId == fbx.FbxAnimLayer.ClassId:
                continue
            else:
                fbx_obj.ConnectDstObject(merged_scene)
        first_scene.DisconnectAllSrcObject()  # DON'T FORGET TO DISCONNECT THE ORIGINAL SCENE FROM THE MOVED OBJECTS!


if __name__ == '__main__':
    LodBoxFbx()
