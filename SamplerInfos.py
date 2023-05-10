import unreal

sampler_infos = {
    'BaseColor': {
        'sampler_type': unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
        'connections': [
            ('RGB', unreal.MaterialProperty.MP_BASE_COLOR)
        ]
    },
    'Normal': {
        'sampler_type': unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
        'connections': [
            ('RGB', unreal.MaterialProperty.MP_NORMAL)
        ],
    },
    'OcclusionRoughnessMetallic': {
        'sampler_type': unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
        'connections': [
            ('R', unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),
            ('G', unreal.MaterialProperty.MP_ROUGHNESS),
            ('B', unreal.MaterialProperty.MP_METALLIC),
        ],
    }
}