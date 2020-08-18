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


def export_fbx(manager, scene, version, filename, file_format):
    """
    Exports scene as FBX file.\n
    See "FBX SDK C++ API Reference > Files > File List > fbxsdk > fileio > fbx" for list of valid inputs for version.

    :param manager: FBX Manager
    :type manager: fbx.FbxManager
    :param scene: FBX Scene
    :type scene: fbx.FbxScene
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
    with Exporter(manager) as lbox_exp:

        # The FbxSceneRenamer() is only used for FBX version, makes sure the string doesn't contain characters the various formats/programs don't like
        scene_renamer = fbx.FbxSceneRenamer(scene)

        # Most of the IO settings are True by default so no need to set any...for now!
        # TODO: Some kind of better sanity checks here
        lbox_exp.exporter.SetFileExportVersion(version, scene_renamer.eFBX_TO_FBX)
        result = lbox_exp.exporter.Initialize(filename, file_format, manager.GetIOSettings())
        if result:
            return lbox_exp.exporter.Export(scene)  # MAKE SURE THIS MATCHES THE INPUT SCENE >(
        else:
            raise IOError


def import_scene(manager, scene, filename):
    """

    :param manager: FBX Manager
    :type manager: fbx.FbxManager
    :param scene: FBX Scene
    :type scene: fbx.FbxScene
    :param filename:
    :type filename: str
    :return: result
    :rtype: bool
    """
    with Importer(manager) as lbox_imp:
        file_format = lbox_imp.importer.GetFileFormat()
        # TODO: Check out FbxCommon.LoadScene() for IOSettings
        result = lbox_imp.importer.Initialize(filename, file_format, manager.GetIOSettings())
        if result:
            return lbox_imp.importer.Import(scene)
        else:
            raise IOError


class Exporter(object):
    """A small wrapper around FbxExporter to turn it
    into a Context Manager.
    """
    def __init__(self, manager, name='LodBoxExporter'):
        self.manager = manager
        self.name = name
        self.exporter = None

    # Since __enter__ method is executed AFTER __init__ ,
    # creation of FbxExporter object is done here (but not initialised).
    def __enter__(self):
        self.exporter = fbx.FbxExporter.Create(self.manager, self.name)  # type: fbx.FbxExporter
        return self

    # Makes sure to destroy the FBX exporter otherwise this would need to be done manually.
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exporter.Destroy()
        self.exporter = None
        return self


class Importer(object):
    """A small wrapper around FbxImporter to turn it
    into a Context Manager.
    """
    def __init__(self, manager, name='LodBoxImporter'):
        self.manager = manager
        self.name = name
        self.importer = None

    def __enter__(self):
        self.importer = fbx.FbxImporter.Create(self.manager, self.name) # type: fbx.FbxImporter
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.importer.Destroy()
        self.importer = None
        return self
