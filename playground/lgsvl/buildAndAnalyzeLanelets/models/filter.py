# Compute input features for all the positive paths
from typing import List
from .correlation.utils import _pairwise as pairs
from .correlation.edit_distance_polyline import iterative_levenshtein, _standardize
from .correlation.illumination_map import IlluminationMap, IlluminationAxisDefinition
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
import math

def _plot_points(points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    # Plot the points
    # x, y = the_points.T
    plt.gca().set_aspect('equal')
    # plt.scatter(x, y)
    plt.plot(x, y, "o")


class Filter:
    @staticmethod
    def compare_distance(routes, dist=1.9):
        similar_routes = list()
        for a, b in pairs(routes):
            it_dist = iterative_levenshtein(a.interpolated_points, b.interpolated_points)

            # This is bounded 0 - 1
            # This seems quite sensitive with only 3 dimensions
            # TODO Probably this cosine similarity may work better if we rescale the vectors
            # FORGET ABOUT COSINE DISTANCE
            # cosine_similarity = 1 - cosine(a.feature_vector, b.feature_vector)

            # print("Comparing ", a["feature_vector"], "-", b["feature_vector"])

            # Plot only the roads that are too similar
            if it_dist < dist:
                # Plot the standardized roads not the original one (they all start at (0,0))
                # std_a = _standardize(a.interpolated_points)
                # std_b = _standardize(b.interpolated_points)
                # _plot_points(std_a)
                # _plot_points(std_b)
                # plt.title("IT Distance {} - Cosine Similarity {}".format(it_dist, cosine_similarity))
                # plt.show()
                similar_routes.append(b)

        return [x for x in routes if (x not in similar_routes)]


    @staticmethod
    def compare_feature(routes):
        # Compute the features for all the paths and store min/max values for each feature
        # Use only 2 Features
        dc_extrema = [math.inf, -math.inf]
        mr_extrema = [math.inf, -math.inf]
        # ct_extrema = [math.inf, -math.inf]

        for route in routes:
            dc_extrema[0] = min(dc_extrema[0], route.dc)
            dc_extrema[1] = max(dc_extrema[1], route.dc)
            mr_extrema[0] = min(mr_extrema[0], route.mr)
            mr_extrema[1] = max(mr_extrema[1], route.mr)

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

            # Showing
            # Register it in the map, so we see the most frequent combinations
            illumination_map.add_sample(sample)

        illumination_map.visualize()
        # plt.show()
        return filtered_routes
