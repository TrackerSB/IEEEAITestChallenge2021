# Compute input features for all the positive paths
from .utils import direction_coverage, min_radius
from .illumination_map import IlluminationMap, IlluminationAxisDefinition
import math
import matplotlib.pyplot as plt


def compare_feature(routes):
    # Compute the features for all the paths and store min/max values for each feature
    # Use only 2 Features
    dc_extrema = [math.inf, -math.inf]
    mr_extrema = [math.inf, -math.inf]
    # ct_extrema = [math.inf, -math.inf]

    for route in routes:
        interpolated_path = route.interpolated_points

        # Compute Feature Direction Coverage
        dc = direction_coverage(interpolated_path)

        dc_extrema[0] = min(dc_extrema[0], dc)
        dc_extrema[1] = max(dc_extrema[1], dc)

        # Compute feature Min Radius
        mr = min(min_radius(interpolated_path), 100)

        mr_extrema[0] = min(mr_extrema[0], mr)
        mr_extrema[1] = max(mr_extrema[1], mr)

        # Not sure this matters too much...
        # ct = count_turns(interpolated_path)
        # ct_extrema[0] = min(ct_extrema[0], ct)
        # ct_extrema[1] = max(ct_extrema[1], ct)

        # p_path["feature_vector"] = [dc, mr, ct]
        route.feature_vector = [dc, mr]

        # Store the feature inside the object
        route.dc = dc
        route.mr = mr

    # Create the feature map - TODO Values needs some adjustment
    direction_coverage_feature = IlluminationAxisDefinition("dc", dc_extrema[0], dc_extrema[1], 10)
    min_radius_feature = IlluminationAxisDefinition("mr", mr_extrema[0], mr_extrema[1], 10)

    illumination_map = IlluminationMap(direction_coverage_feature, min_radius_feature)

    filtered_routes = list()
    for sample in routes:
        # Try to add the element to the map
        # Filtering
        if illumination_map.is_cell_free(sample):
            filtered_routes.append(sample)
        else:
            print("DISCARD VALUE. ALREADY IN MAP")
            # TODO Get rid of the path, so do not execute this one

        # Showing
        # Register it in the map, so we see the most frequent combinations
        illumination_map.add_sample(sample)

    # illumination_map.visualize()
    # plt.show()
    return filtered_routes
