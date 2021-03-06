from __future__ import annotations

from dataclasses import dataclass

from slicereg.commands.base import BaseSectionRepo, BaseCommand
from slicereg.commands.utils import Signal
from slicereg.repos.atlas_repo import BaseAtlasRepo
from slicereg.models.registration import register

@dataclass
class UpdateSectionTransformCommand(BaseCommand):
    _section_repo: BaseSectionRepo
    _atlas_repo: BaseAtlasRepo
    section_moved: Signal = Signal()

    def __call__(self, **dims):  # type: ignore
        for dim in dims:
            if dim not in ['right', 'superior', 'anterior', 'rot_lateral', 'rot_axial', 'rot_median']:
                raise TypeError(f'Unknown dimension "{dim}"')

        sections = self._section_repo.sections
        atlas = self._atlas_repo.get_atlas()
        if not sections:
            raise RuntimeError('Section is not loaded yet')
        if not atlas:
            raise RuntimeError('Atlas is not loaded yet')
        section = sections[0]
                
        new_section = section.set_plane_3d(**dims)
        atlas_section = register(section=new_section, atlas=atlas)
        self._section_repo.save_section(new_section)
        self.section_moved.emit(transform=new_section.affine_transform, atlas_slice_image=atlas_section.image.channels[0])
