import unreal
from SamplerInfos import sampler_infos

def get_material_name(texture_path_name):
    try:
        last_dot_index = texture_path_name.rfind(".")
        new_texture_path_name = texture_path_name[:last_dot_index] 
        last_underscore_index = new_texture_path_name.rfind("_")
        name = texture_path_name[:last_underscore_index]
        return name
    except Exception as e:
        raise Exception("Error defining material name. " + e)

def create_sampler(material, texture_name, sampler_y_pos):
    sampler_name = texture_name[texture_name.rfind("_")+1:]
    
    try:
        sampler_info = sampler_infos[sampler_name]
    except Exception:
        raise Exception("Could not define map type of texture: " + sampler_name)
    
    if(sampler_info) :
        sampler = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionTextureSample, -350, sampler_y_pos)
        sampler.texture = unreal.load_asset(texture_name)
        sampler.sampler_type = sampler_info['sampler_type']

        for connection in sampler_info['connections']:
            unreal.MaterialEditingLibrary.connect_material_property(sampler, connection[0], connection[1])

def create_empty_material_asset(name) -> unreal.Material:
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    out_package_name, out_asset_name = asset_tools.create_unique_asset_name(name, '')
    package_path = out_package_name.rsplit('/', 1)[0]
    asset_name = out_package_name.rsplit('/', 1)[1]
    return asset_tools.create_asset(asset_name, package_path, unreal.Material, unreal.MaterialFactoryNew())

def create_samplers_from_textures(selected_textures, empty_material):
    samplers_count = 0
    sampler_y_pos = -300
    try: 
        for texture in selected_textures:
            if isinstance(texture, unreal.Texture):
                create_sampler(empty_material, texture.get_path_name(), sampler_y_pos)
                samplers_count += 1
                sampler_y_pos += 300
        if(samplers_count == 0):
            raise Exception("No textures selected")

    except Exception as e:
        unreal.EditorAssetLibrary.delete_asset(empty_material.get_path_name())
        raise Exception(str(e))

def create_texture_dict(selected_textures):
    texture_dict = {}
    for texture in selected_textures:
        name = get_material_name(texture.get_path_name())
        if name in texture_dict:
            texture_dict[name].append(texture)
        else:
            texture_dict[name] = [texture]
    return texture_dict

def create_material_from_selected():
    try :
        selected_textures = unreal.EditorUtilityLibrary.get_selected_assets()
        
        if (len(selected_textures) == 0):
            raise Exception("Nothing selected")
        
        texture_dict = create_texture_dict(selected_textures)
        for material_name, texture_list in texture_dict.items():
            material = create_empty_material_asset(material_name)
            create_samplers_from_textures(texture_list, material)
            unreal.MaterialEditingLibrary.recompile_material(material)
            unreal.EditorAssetLibrary.save_asset(material.get_path_name())        
    except Exception as e:            
        unreal.log_error(e)

create_material_from_selected()