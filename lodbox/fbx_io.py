import fbx

# I got these string from fbxio.h (which works in 2015)
# in FBX SDK Reference > Files > File List > fbxsdk > fileio > fbx
FBX_VERSION = {'2010': "FBX201000",
               '2011': "FBX201100",
               '2012': "FBX201200",
               '2013': "FBX201300",
               '2014': "FBX201400",
               '2016': "FBX201600",
               '2018': "FBX201800",
               '2019': "FBX201900"
               }

# ASCII=1 for pFileformat and -1/0/1 is Binary
# Look into FbxIOPluginRegistry for more info
FBX_FORMAT = {'Binary': -1,
              'ASCII': 1
              }


def export_fbx(fbx_manager, fbx_scene, version, filename, file_format):
    """
    Exports scene as FBX file.\n
    See "FBX SDK C++ API Reference > Files > File List > fbxsdk > fileio > fbx" for list of valid inputs for version.

    :param fbx_manager: FBX Manager
    :type fbx_manager: fbx.FbxManager
    :param fbx_scene: FBX Scene
    :type fbx_scene: fbx.FbxScene
    :param version: FBX File Version
    :type version: str
    :param filename: Export file name (without file extension)
    :type filename: str
    :param file_format: Which format the exported file should be. When FBX, it is either ASCII or Binary (Binary is default)
    :type file_format: int
    :return: result
    :rtype: bool
    """
    # Export the file. Same process as importing - Create the Exporter, Initialize it, export!
    exporter = fbx.FbxExporter.Create(fbx_manager, 'Exporter')  # type: fbx.FbxExporter

    # The FbxSceneRenamer() is only used for FBX version, makes sure the string doesn't contain characters the various formats/programs don't like
    scene_renamer = fbx.FbxSceneRenamer(fbx_scene)

    # Most of the IO settings are True by default so no need to set any...for now!
    # I got this string from fbxio.h (which works in 2015) in FBX SDK Reference > Files > File List > fbxsdk > fileio > fbx
    exporter.SetFileExportVersion(version, scene_renamer.eFBX_TO_FBX)
    # TODO: Some kind of sanity check here!
    exporter.Initialize(filename, file_format, fbx_manager.GetIOSettings())
    exporter.Export(fbx_scene)  # MAKE SURE THIS MATCHES THE INPUT SCENE >(
    print(exporter.GetFileName())
    exporter.Destroy()  # Make sure to destroy the scene exporter afterwards!
