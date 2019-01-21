import fbx

FBX_VERSION = {'2010': "201000",
               '2011': "201100",
               '2012': "201200",
               '2013': "201300",
               '2014': "201400",
               '2016': "201600",
               '2018': "201800"
               }


def export_fbx(fbx_manager, fbx_scene, version, filename):
    """
    Exports scene as FBX file.\n
    See "FBX SDK C++ API Reference > Files > File List > fbxsdk > fileio > fbx" for list of valid inputs for version.

    :param fbx_manager: FBX Manager
    :type fbx_manager: fbx.FbxManager
    :param fbx_scene: FBX Scene
    :type fbx_scene: fbx.FbxScene
    :param version: FBX File Version
    :type version: str
    :param filename: Export file name
    :type filename: str
    :return:
    :rtype: None
    """
    # Export the file. Same process as importing - Create the Exporter, Initialize it, export!
    exporter = fbx.FbxExporter.Create(fbx_manager, 'Exporter')  # type: fbx.FbxExporter

    # The FbxSceneRenamer() is only used for FBX version, makes sure the string doesn't contain characters the various formats/programs don't like
    scene_renamer = fbx.FbxSceneRenamer(fbx_scene)

    # Most of the IO settings are True by default so no need to set any...for now!
    # I got this string from fbxio.h (which works in 2015) in FBX SDK Reference > Files > File List > fbxsdk > fileio > fbx
    exporter.SetFileExportVersion(version, scene_renamer.eFBX_TO_FBX)
    # ASCII=2 for pFileformat and -1/0/1 is Binary
    # Look into FbxIOPluginRegistry for more info
    exporter.Initialize(filename, -1, fbx_manager.GetIOSettings())
    exporter.Export(fbx_scene)  # MAKE SURE THIS MATCHES THE INPUT SCENE >(
    exporter.Destroy()  # Make sure to destroy the scene exporter afterwards!
