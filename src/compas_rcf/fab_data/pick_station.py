from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from compas.geometry import Frame
from compas.geometry import Transformation

log = logging.getLogger(__name__)


class PickStation(object):
    """Picking station setup."""

    def __init__(self, pick_frames):
        """Init function for PickSetup.

        Parameters
        ----------
        plate_frames : list of :class:`compas.geometry.Frame`
            List of picking frames
        """
        self.pick_frames = pick_frames
        self.counter = 0
        self.n_pick_frames = len(pick_frames)

    def get_next_frame(self, place_cylinder):
        """Get next frame to pick cylinder at.

        Parameters
        ----------
        cylinder : :class:`compas_rcf.fab_data.Claycylinder`
            cylinder to place

        Returns
        -------
        :class:`compas.geometry.Frame`
        """
        idx = self.counter % self.n_pick_frames
        self.counter += 1

        log.debug("Counter at: {}, Frame index at {}".format(self.counter, idx))

        pick_location = self.pick_frames[idx]

        T = Transformation.from_frame_to_frame(place_cylinder.location, pick_location)

        # Copy place_cylinder to get same height properties
        pick_cylinder = place_cylinder.copy()
        pick_cylinder.location.transform(T)

        return pick_cylinder

    @classmethod
    def from_data(cls, data):
        """TODO: Docstring for function.

        Parameters
        ----------
        data : :obj:`dict`

        Returns
        -------
        :class:`PickStation`
        """
        frames = [Frame.from_data(frame_data) for frame_data in data]

        return cls(frames)
