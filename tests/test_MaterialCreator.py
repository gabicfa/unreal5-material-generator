import pytest
import MaterialCreator
import unreal
import unittest.mock as mock
import traceback
from SamplerInfos import sampler_infos


@pytest.fixture
def mocked_texture(mocker):
    # Create a mock object for unreal.Texture
    mock_texture = mocker.Mock(spec=unreal.Texture)
    return mock_texture

@pytest.fixture
def mocked_empty_material(mocker):
    # Create a mock object for unreal.Material
    mock_empty_material = mocker.Mock(spec=unreal.Material)
    return mock_empty_material

@pytest.fixture
def mocked_asset_tools(mocker):
    # Create a mock object for AssetToolsHelpers
    mock_asset_tools = mocker.Mock()
    
    # Configure the create_unique_asset_name() method of the mock asset tools
    mock_asset_tools.create_unique_asset_name.return_value = ('/Game/Assets/Textures/AssetName', 'AssetName')
    
    # Create a mock object for unreal.Material
    mocked_material = mocker.Mock(spec=unreal.Material)
    
    # Configure the create_asset() method of the mock asset tools to return the mocked material
    mock_asset_tools.create_asset.return_value = mocked_material
    
    return mock_asset_tools

def test_get_material_name():
    # Test cases
    test_cases = [
        {
            'texture_path': '/Game/Assets/Textures/AssetName_BaseColor.AssetName_BaseColor',
            'expected_result': '/Game/Assets/Textures/AssetName'
        },
        {
            'texture_path': '/Game/Assets/Textures/AssetName_Normal.Asset_Normal',
            'expected_result': '/Game/Assets/Textures/AssetName'
        },
        {
            'texture_path': '/Game/Assets/Textures/AssetName_OcclusionRoughnessMetallic.AssetName_OcclusionRoughnessMetallic',
            'expected_result': '/Game/Assets/Textures/AssetName'
        }
    ]
    
    # Execute the test cases
    for test_case in test_cases:
        texture_path = test_case['texture_path']
        expected_result = test_case['expected_result']        

        # Call the function under test
        result = MaterialCreator.get_material_name(texture_path)

        # Assertions
        assert result == expected_result

def test_create_texture_dict(mocker):
    # Configure the behavior of get_material_name mock
    get_material_name_mock = mocker.Mock(side_effect=[
        'AssetName_Base', 'AssetName_Base', 'AssetName_Normal'
    ])

    # Patch the get_material_name function with the mock
    mocker.patch('MaterialCreator.get_material_name', new=get_material_name_mock)

    # Create mock texture objects
    texture1 = mocker.Mock(spec=unreal.Texture2D)
    texture2 = mocker.Mock(spec=unreal.Texture2D)
    texture3 = mocker.Mock(spec=unreal.Texture2D)

    # Create the list of selected textures
    selected_textures = [texture1, texture2, texture3]

    # Call the function under test
    result = MaterialCreator.create_texture_dict(selected_textures)

    # Assertions
    assert len(result) == 2  # Expecting two different material names

    assert 'AssetName_Base' in result
    assert len(result['AssetName_Base']) == 2  # Expecting two textures with 'AssetName_Base' material name
    assert result['AssetName_Base'] == [texture1, texture2]

    assert 'AssetName_Normal' in result
    assert len(result['AssetName_Normal']) == 1  # Expecting one texture with 'AssetName_Normal' material name
    assert result['AssetName_Normal'] == [texture3]

def test_create_empty_material_asset(mocked_asset_tools, mocker):
    # Patch the get_asset_tools() method to return the mock asset tools
    mocker.patch('unreal.AssetToolsHelpers.get_asset_tools', return_value=mocked_asset_tools)
    
    # Call the function under test
    result = MaterialCreator.create_empty_material_asset('/Game/Assets/Textures/AssetName')
    
    # Assertions
    assert isinstance(result, unreal.Material)

def test_create_samplers_from_textures(mocked_texture, mocked_empty_material, mocker):
    # Configure the behavior of mocked_texture.get_path_name()
    mocked_texture.get_path_name.side_effect = [
    '/Game/Assets/Textures/AssetName_BaseColor.AssetName_BaseColor',
    '/Game/Assets/Textures/AssetName_Normal.AssetName_Normal',
    '/Game/Assets/Textures/AssetName_OcclusionRoughnessMetallic.AssetName_OcclusionRoughnessMetallic'
    ]
    
    # Patch the create_sampler() function
    mock_create_sampler = mocker.patch('MaterialCreator.create_sampler')

    # Patch the delete_asset() function
    mock_delete_asset = mocker.patch('unreal.EditorAssetLibrary.delete_asset')

    # Call the function under test
    try:
        MaterialCreator.create_samplers_from_textures([mocked_texture, mocked_texture, mocked_texture], mocked_empty_material)
    except Exception as e:
        traceback.print_exc()

    # Assertions
    expected_calls = [
        mocker.call(mocked_empty_material, '/Game/Assets/Textures/AssetName_BaseColor.AssetName_BaseColor', -300),
        mocker.call(mocked_empty_material, '/Game/Assets/Textures/AssetName_Normal.AssetName_Normal', 0),
        mocker.call(mocked_empty_material, '/Game/Assets/Textures/AssetName_OcclusionRoughnessMetallic.AssetName_OcclusionRoughnessMetallic', 300)
    ]
    mock_create_sampler.assert_has_calls(expected_calls)
    assert not mock_delete_asset.called
    
def test_create_samplers_from_textures_no_textures(mocked_empty_material, mocker):
    # Patch the delete_asset() function
    mock_delete_asset = mocker.patch('unreal.EditorAssetLibrary.delete_asset')
    
    # Call the function under test
    with pytest.raises(Exception) as exc_info:
        MaterialCreator.create_samplers_from_textures([], mocked_empty_material)

    # Assertions
    assert str(exc_info.value) == "No textures selected"
    mock_delete_asset.assert_called_once_with(mocked_empty_material.get_path_name())

def test_create_sampler(mocker):
    # Mock the required objects and functions
    mock_material = mocker.Mock(spec=unreal.Material)
    mock_texture = mocker.Mock(spec=unreal.Texture)
    
    # Patch the sampler_infos dictionary
    mocker.patch('MaterialCreator.sampler_infos', new=sampler_infos)
    
    mocker.patch('unreal.MaterialEditingLibrary.create_material_expression', return_value=mock.Mock())
    mocker.patch('unreal.load_asset', return_value=mock_texture)
    mocker.patch('unreal.MaterialEditingLibrary.connect_material_property')

    # Call the function under test for each sampler info
    for sampler_name, sampler_info in sampler_infos.items():
        texture_name = f'/Game/Textures/AssetName_{sampler_name}.AssetName_{sampler_name}'
        sampler_y_pos = -300  # You can modify the Y position as needed
        
        MaterialCreator.create_sampler(mock_material, texture_name, sampler_y_pos)

        # Assertions
        unreal.MaterialEditingLibrary.create_material_expression.assert_called_with(
            mock_material, unreal.MaterialExpressionTextureSample, -350, sampler_y_pos
        )
        unreal.load_asset.assert_called_with(texture_name)
        unreal.MaterialEditingLibrary.connect_material_property.assert_has_calls(
            mock.call(mock.ANY, connection[0], connection[1]) for connection in sampler_info['connections']
        )
        sampler_y_pos += 300

def test_create_material_from_selected_no_selection(mocker):
    # Patch the get_selected_assets() function to return an empty list
    mocker.patch('unreal.EditorUtilityLibrary.get_selected_assets', return_value=[])

    # Patch the log_error() function
    mock_log_error = mocker.patch('unreal.log_error')

    # Call the function under test
    MaterialCreator.create_material_from_selected()

    # Assertions
    mock_log_error.assert_called_once_with("Nothing selected")


def test_create_material_from_selected_with_selection(mocker):
    # Create mock objects for selected textures
    mock_texture1 = mocker.Mock(spec=unreal.Texture2D)
    mock_texture2 = mocker.Mock(spec=unreal.Texture2D)
    mock_texture3 = mocker.Mock(spec=unreal.Texture2D)

    # Patch the get_selected_assets() function to return the mock texture objects
    mocker.patch('unreal.EditorUtilityLibrary.get_selected_assets', return_value=[mock_texture1, mock_texture2, mock_texture3])

    # Create mock texture dictionary
    mock_texture_dict = {
        'Material1': [mock_texture1, mock_texture2],
        'Material2': [mock_texture3]
    }

    # Patch the create_texture_dict() function to return the mock texture dictionary
    mocker.patch('MaterialCreator.create_texture_dict', return_value=mock_texture_dict)

    # Create mock material objects
    mock_material1 = mocker.Mock(spec=unreal.Material)
    mock_material2 = mocker.Mock(spec=unreal.Material)

    # Patch the create_empty_material_asset() function to return the mock material objects
    mocker.patch('MaterialCreator.create_empty_material_asset', side_effect=[mock_material1, mock_material2])

    # Patch the create_samplers_from_textures() function
    mock_create_samplers = mocker.patch('MaterialCreator.create_samplers_from_textures')

    # Patch the recompile_material() function
    mock_recompile_material = mocker.patch('unreal.MaterialEditingLibrary.recompile_material')

    # Patch the save_asset() function
    mock_save_asset = mocker.patch('unreal.EditorAssetLibrary.save_asset')

    # Call the function under test
    MaterialCreator.create_material_from_selected()

    # Assertions
    assert mock_create_samplers.call_count == 2  # Two different material names
    mock_create_samplers.assert_any_call([mock_texture1, mock_texture2], mock_material1)
    mock_create_samplers.assert_any_call([mock_texture3], mock_material2)

    mock_recompile_material.assert_has_calls([
        mocker.call(mock_material1),
        mocker.call(mock_material2)
    ])
    mock_save_asset.assert_has_calls([
        mocker.call(mock_material1.get_path_name.return_value),
        mocker.call(mock_material2.get_path_name.return_value)
    ])