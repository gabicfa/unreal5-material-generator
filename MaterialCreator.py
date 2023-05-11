import unreal
from SamplerInfos import sampler_infos

def get_material_name(texture_path: str) -> str:
    """
    Extracts the material name from a texture path.

    Args:
        texture_path: A string representing the texture path.

    Returns:
        A string representing the material name.
    """
    try:
        last_dot_index = texture_path.rfind('.')
        new_texture_path = texture_path[:last_dot_index]
        last_underscore_index = new_texture_path.rfind('_')
        name = texture_path[:last_underscore_index]
        return name
    except Exception as e:
        raise ValueError(f"Error defining material name. {e}")

def create_sampler(material: unreal.Material, texture_name: str, sampler_y_pos: float) -> None:
    """
    Creates a new sampler expression in the material for the specified texture.

    Args:
        material: An instance of unreal.Material.
        texture_name: A string representing the texture name.
        sampler_y_pos: A float representing the vertical position of the sampler expression.

    Raises:
        Exception: If the sampler info for the specified texture name cannot be found.
    """
    # Extract the name of the sampler from the texture name
    sampler_name = texture_name[texture_name.rfind('_')+1:]
    try:
        # Look up the sampler info for this sampler name
        sampler_info = sampler_infos[sampler_name]
    except Exception:
        raise Exception(f"Could not define map type of texture: {sampler_name}")
    
    if sampler_info:
        # Create a new sampler expression in the material
        sampler = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionTextureSample, -350, sampler_y_pos)
        # Load the texture asset and set it as the texture input for the sampler
        sampler.texture = unreal.load_asset(texture_name)
        # Set the sampler type based on the sampler info
        sampler.sampler_type = sampler_info['sampler_type']

        # Connect any additional inputs based on the sampler info
        for connection in sampler_info['connections']:
            unreal.MaterialEditingLibrary.connect_material_property(sampler, connection[0], connection[1])

def create_empty_material_asset(name: str) -> unreal.Material:
    """
    Creates an empty material asset with the specified name.

    Args:
        name: A string representing the name of the material asset.

    Returns:
        An instance of unreal.Material representing the newly created material asset.
    """
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    out_package_name, out_asset_name = asset_tools.create_unique_asset_name(name, '')
    package_path = out_package_name.rsplit('/', 1)[0]
    asset_name = out_package_name.rsplit('/', 1)[1]
    return asset_tools.create_asset(asset_name, package_path, unreal.Material, unreal.MaterialFactoryNew())

# @brief creates semplers in material blueprint
# Modified from :
# Unreal engine (2022). Simplifying Tool Creation with Blueprints & Python | Inside Unreal [video, online]. 
# YouTube. Available from: https://www.youtube.com/live/mwc4NsB70lo?feature=share [Accessed 11 May 2023] 
def create_samplers_from_textures(selected_textures: list, empty_material: unreal.Material) -> None:
    """
    Creates samplers for a list of textures in an empty material.

    Args:
        selected_textures: A list of instances of unreal.Texture.
        empty_material: An instance of unreal.Material representing an empty material asset.

    Raises:
        Exception: If no textures are selected.
    """
    samplers_count = 0
    sampler_y_pos = -300
    try:
        for texture in selected_textures:
            if isinstance(texture, unreal.Texture):
                create_sampler(empty_material, texture.get_path_name(), sampler_y_pos)
                samplers_count += 1
                sampler_y_pos += 300
# end of Citation
        if samplers_count == 0:
            raise Exception("No textures selected")
    except Exception as e:
        # If an exception is raised, delete the empty material and re-raise
        unreal.EditorAssetLibrary.delete_asset(empty_material.get_path_name())
        raise Exception(str(e))

def create_texture_dict(selected_textures : list):
    """
    Groups a list of textures by their material name.

    Args:
        selected_textures (list): A list of texture assets to group by material name.

    Returns:
        A dictionary containing lists of textures grouped by their material name.
    """
    texture_dict = {}
    for texture in selected_textures:
        # Get the name of the material from the texture path
        name = get_material_name(texture.get_path_name())
        if name in texture_dict:
            texture_dict[name].append(texture)
        else:
            texture_dict[name] = [texture]
    return texture_dict


def create_material_from_selected():
    """
    Creates a new material asset for each group of selected textures.

    Raises:
        Exception: If no textures are selected or if an error occurs while creating a material.
    """
    try:
        # Get the list of selected assets in the content browser
        selected_textures = unreal.EditorUtilityLibrary.get_selected_assets()

        if len(selected_textures) == 0:
            # If nothing is selected, raise an exception
            raise Exception("Nothing selected")

        # Group the selected textures by material name
        texture_dict = create_texture_dict(selected_textures)

        # Create a new material asset for each group of textures
        for material_name, texture_list in texture_dict.items():
            # Create an empty material asset
            material = create_empty_material_asset(material_name)

            # Create samplers for the textures and add them to the material
            create_samplers_from_textures(texture_list, material)

            # Recompile the material to apply changes
            unreal.MaterialEditingLibrary.recompile_material(material)

            # Save the material asset
            unreal.EditorAssetLibrary.save_asset(material.get_path_name())
    except Exception as e:
        # If an exception is raised, log the error
        unreal.log_error(str(e))

# Call the main function to create materials from selected textures
create_material_from_selected()