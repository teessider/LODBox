import abc
import os
from pathlib import Path
from typing import Optional
from enum import IntEnum

import fbx

# I got these string from fbxio.h (which works in 2015)
# in FBX SDK Reference > Files > File List > fbxsdk > fileio > fbx
FBX_VERSION = {
    2010: "FBX201000",
    2011: "FBX201100",
    2012: "FBX201200",
    2013: "FBX201300",
    2014: "FBX201400",
    2016: "FBX201600",
    2018: "FBX201800",
    2019: "FBX201900",
    2020: "FBX202000"
    }


# ASCII=1 for pFileformat and -1/0 is Binary
# Look into FbxIOPluginRegistry for more info
class LodBoxFbxFormat(IntEnum):
    BINARY = 0
    ASCII = 1


def export_scene_fbx(manager: fbx.FbxManager, scene: fbx.FbxScene, fbx_version: str, file_path: Path, file_format: LodBoxFbxFormat) -> bool:
    """
    Exports scene as FBX file.

    See "FBX SDK C++ API Reference > Files > File List > fbxsdk > fileio > fbx" for list of valid inputs for version.

    Args:
        manager: FBX Manager
        scene: FBX Scene
        fbx_version: FBX File Version in the format: "FBXYEAR00" (FBX201900 for example). Can use FBX_VERSION module dictionary.
        file_path: Export file name (without file extension)
        file_format: Which format the exported file should be. When FBX, it is either ASCII or Binary (Binary is default)

    Returns:
        result: True if the FBX is exported successfully

    Raises:
        IOError: An error has occurred when trying to export the FBX file
    """
    # Export the file. Same process as importing - Create the Exporter, Initialize it, export!
    with Exporter(manager) as lbox_exp:

        # The FbxSceneRenamer() is only used for FBX version, makes sure the string doesn't contain characters the various formats/programs don't like
        scene_renamer = fbx.FbxSceneRenamer(scene)

        # Most of the IO settings are True by default so no need to set any...for now!
        # TODO: Some kind of better sanity checks here
        lbox_exp.exporter.SetFileExportVersion(fbx_version, scene_renamer.eFBX_TO_FBX)
        result = lbox_exp.exporter.Initialize(file_path, file_format, manager.GetIOSettings())
        if result:
            return lbox_exp.exporter.Export(scene)  # MAKE SURE THIS MATCHES THE INPUT SCENE >(
        else:
            status: fbx.FbxStatus = lbox_exp.exporter.GetStatus()
            print(status.GetCode())
            # TODO: raise pythonic error here?
            # raise IOError
            return False



# TODO: TRY AS CONTEXT MANAGER FUNCTION INSTEAD OF USING A CLASS ??
def import_scene(manager: fbx.FbxManager, scene: fbx.FbxScene, file_path: os.PathLike) -> bool:
    """
    Args:
        manager: FBX Manager
        scene: FBX Scene
        file_path: Path to File

    Returns:
        result: True if the file is imported successfully
    Raises:
        IOError: An error has occurred when trying to import the FBX file
    """
    with Importer(manager) as lbox_imp:
        file_format: int = lbox_imp.importer.GetFileFormat()
        # TODO: Check out FbxCommon.LoadScene() for IOSettings
        result = lbox_imp.importer.Initialize(file_path, file_format, manager.GetIOSettings())
        status: fbx.FbxStatus = lbox_imp.importer.GetStatus()
        if result:
            print(status.GetCode())
            return lbox_imp.importer.Import(scene)
        else:
            # Unfortunately it seems the importer only produces one code (eFailure)
            print(status.GetCode(), type(status.GetCode()),
                  status.GetErrorString(), status.Error())
            if status.Error():
                if status.GetErrorString() == "Uninitialized filename" and status.GetErrorString() == "Unexpected file type":
                    raise FileNotFoundError(status.GetErrorString())
            return False


class LodBoxFbxIOBase(abc.ABC):
    def __init__(self, manager: fbx.FbxManager, name):
        self.manager = manager
        self.name = name


class Exporter(LodBoxFbxIOBase):
    """A small wrapper around FbxExporter to turn it
    into a Context Manager.
    """
    def __init__(self, manager: fbx.FbxManager, name='LodBoxFbxExporter'):
        super().__init__(manager=manager, name=name)
        self.exporter: Optional[fbx.FbxExporter] = None

    # Since __enter__ method is executed AFTER __init__ ,
    # creation of FbxExporter object is done here (but not initialised).
    def __enter__(self):
        self.exporter = fbx.FbxExporter.Create(self.manager, self.name)
        return self

    # Makes sure to destroy the FBX exporter otherwise this would need to be done manually.
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exporter.Destroy()
        self.exporter = None
        return self


class Importer(LodBoxFbxIOBase):
    """A small wrapper around FbxImporter to turn it
    into a Context Manager.
    """
    def __init__(self, manager: fbx.FbxManager, name='LodBoxFbxImporter'):
        super().__init__(manager=manager, name=name)
        self.importer: Optional[fbx.FbxImporter] = None

    def __enter__(self):
        self.importer = fbx.FbxImporter.Create(self.manager, self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.importer.Destroy()
        self.importer = None
        return self
