"""WattToWater: a water meter for code.

Shows how many litres of water a compute job uses in 11 data-center regions, split into
on-site cooling water and off-site water used to generate electricity, next to each
region's baseline water stress.

    from watttowater import track_water, recommend_regions, compare

All numbers are estimates for comparison, not measurements of any real facility.
"""

from .advisor import compare, print_regions, recommend_regions
from .data import REGIONS, STRESS, water_for
from .meter import measure
from .report import summarize
from .tracker import track_water

__version__ = "0.1.0"
__all__ = ["track_water", "recommend_regions", "print_regions", "compare", "summarize",
           "measure", "water_for", "REGIONS", "STRESS"]
