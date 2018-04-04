from __future__ import print_function
import sys
from PIL import Image
import fbx


def find_textures_on_nodes(node, texture_dictionary, current_path):
    current_path.append(node.GetName())
    # print("Path: {}".format(current_path))

    # See what node uses what materials!
    for material_index in range(0, node.GetMaterialCount()):
        material = node.GetMaterial(material_index)
        # print("\tMaterial: {}".format(material.GetName()))

        # Access the material's properties
        # fbx.FbxLayerElement.sTypeTextureCount() provides number of texture base properties
        for property_index in range(0, fbx.FbxLayerElement.sTypeTextureCount()):
            property = material.FindProperty(fbx.FbxLayerElement.sTextureChannelNames(property_index))

            # Some of the texture base properties are nameless so they will be filtered
            # if property.GetName() != '':
            #     print("\t\tProperty: {}".format(property.GetName()))

            # Now to obtain the connected textures
            for texture_index in range(0, property.GetSrcObjectCount(fbx.FbxFileTexture.ClassId)):
                texture_obj = property.GetSrcObject(fbx.FbxFileTexture.ClassId, texture_index)
                # print("\t\t\tTexture: {}".format(texture_obj.GetFileName()))

                #  Now to only print the paths to the invalid textures
                texture_obj_filename = texture_obj.GetFileName()
                if texture_obj_filename in texture_dictionary.keys():
                    tex_width, tex_height = texture_dictionary[texture_obj_filename]

                    print('Texture ({}x{}) found at: {} > {} > {} > \"{}\"'.format(tex_width, tex_height, current_path,
                                                                                   material.GetName(), property.GetName(), texture_obj_filename))

    # This just returns the children of the current node without context of materials
    for x in range(0, node.GetChildCount()):
        find_textures_on_nodes(node.GetChild(x), texture_dictionary, current_path)  # A little bit of recursion here!

    current_path.pop()  # This along with the append ensures the correct names are given at any given depth of a scene hierarchy


# # PROGRAM START # #
filepath = "cubeMan.fbx"  # Hard coded filepath and name for testing

# In FbxCommon.py, some of the following functions/variables have been packaged into functions already!
# Fbx Classes need to initialised with their static Create() method
# Also a note on using the SDK, it's not very Pythonic :| so for loops are like other languages:
# for x in range(0, Something.GetCount()):
#   child = Something.GetChild(x)
#   DoStuff(child)

# Need the SDK manager - handles C++ Memory management
manager = fbx.FbxManager.Create()

# This is used for loading FBXs
importer = fbx.FbxImporter.Create(manager, 'myImporter')
status = importer.Initialize(filepath)  # This where the FBX file is loaded in - we pass that as an argument (as a string)!
if not status:
    print("FbxImporter initialization failed.\n"
          "Error: {}").format(importer.GetStatus().GetErrorString())  #
    sys.exit(0)

# Time to create a 'scene' and import the loaded FBX, in this case the importer object needs to be explicitly destroyed using the Destroy() function
scene = fbx.FbxScene.Create(manager, 'myScene')
importer.Import(scene)
importer.Destroy()

# Obtain all the textures in our scene
# This is an instance where the arguments are different between the C++ SDK and the Python Bindings (FillTextureArray())
texture_array = fbx.FbxTextureArray()
scene.FillTextureArray(texture_array)

# Want to check if the textures are within the specified valid texture dimensions
valid_texture_dimensions = [(256, 256), (512, 512)]
invalid_textures = {}
for i in range(0, texture_array.GetCount()):
    texture = texture_array.GetAt(i)  # This enables access to the texture at that point in the array.
    if texture.ClassId == fbx.FbxFileTexture.ClassId:  # There are multiple types of Texture in FBXs
        texture_filename = texture.GetFileName()
        # OPEN TEXTURE WITH PILLOW
        image = Image.open(texture_filename)
        width, height = image.size

        if (width, height) not in valid_texture_dimensions:
            invalid_textures[texture_filename] = (width, height)

            print("Invalid texture dimensions {}x{} - {}".format(width, height, texture_filename))

# THIS PRODUCES AN ERROR BECAUSE OF LACK OF ARGUMENT :|
find_textures_on_nodes(scene.GetRootNode(), invalid_textures)
