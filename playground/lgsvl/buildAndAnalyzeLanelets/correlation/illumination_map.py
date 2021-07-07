# This module contains the code to create maps
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt

import itertools

# For plotting
import seaborn as sns

import logging
import statistics
import time


def manhattan(coords_ind1, coords_ind2):
    return abs(coords_ind1[0] - coords_ind2[0]) + abs(coords_ind1[1] - coords_ind2[1])

class IlluminationAxisDefinition:

    """
        Data structure that model one axis of the map. In general a map can have multiple axes, even if we visualize
        only a subset of them. On axis usually correspond to a feature to explore.

        For the moment we assume that each axis is equally split in `num_cells`
    """

    def __init__(self, feature_name, min_value, max_value, num_cells):
        self.logger = logging.getLogger('illumination_map.IlluminationAxisDefinition')
        self.logger.debug('Creating an instance of IlluminationAxisDefinition for feature %s', feature_name)

        self.feature_name = feature_name
        self.min_value = min_value
        self.max_value = max_value
        self.num_cells = num_cells
        # Definition of the inner map, values might fall outside it if less than min
        self.original_bins = np.linspace(min_value, max_value, num_cells)
        # Definition of the outer map
        # Include the default boundary conditions. Note that we do not add np.PINF, but the max value.
        # Check: https://stackoverflow.com/questions/4355132/numpy-digitize-returns-values-out-of-range
        self.bins = np.concatenate(([np.NINF], self.original_bins, [max_value+0.001]))

    def get_bins_labels(self):
        """
        Note that here we return explicitly the last bin
        Returns: All the bins plus the default

        """
        return self.original_bins

    def get_coordinate_for(self, sample):
        """
        Return the coordinate of this sample according to the definition of this axis. It triggers exception if the
            sample does not declare a field with the name of this axis, i.e., the sample lacks this feature

        Args:
            sample:

        Returns:
            an integer representing the coordinate of the sample in this dimension

        Raises:
            an exception is raised if the sample does not contain the feature
        """

        # TODO Check whether the sample has the feature
        value = getattr(sample, self.feature_name)

        if value < self.min_value:
            self.logger.warning("Sample %s has value %s below the min value %s for feature %s",
                                sample.id, value, self.min_value, self.feature_name)
        elif value > self.max_value:
            self.logger.warning("Sample %s has value %s above the max value %s for feature %s",
                                sample.id, value, self.max_value, self.feature_name)

        return np.digitize(value, self.original_bins, right=False)

    def is_outlier(self, sample):
        value = sample[self.feature_name]
        return value < self.min_value or value > self.max_value

    def to_dict(self):
        the_dict = {
            "name" : self.feature_name,
            "min-value" : self.min_value,
            "max-value": self.max_value,
            "num-cells": self.num_cells
        }

        return the_dict


class IlluminationMap:
    """
        Data structure that represent a map. The map is defined in terms of its axes
    """
    def __init__(self, feature1: IlluminationAxisDefinition, feature2: IlluminationAxisDefinition):
        """
        Note that axes are positional, the first [0] is x, the second[1] is y, the third [2] is z, etc.
        Args:
            axes:
        """
        self.logger = logging.getLogger('illumination_map.IlluminationMapDefinition')

        self.feature_x = feature1
        self.feature_y = feature2

        self.samples = set()

        # Since we consider only input features we do not care aboutr misbehaviors here
        self.coverage_data = np.zeros(shape=(feature1.num_cells, feature2.num_cells), dtype=int)

    # def _compute_maps_data(self, feature1, feature2, samples):
    #     """
    #     Create the raw data for the map by placing the samples on the map and counting for each cell how many samples
    #     are there and how many misbehaviors
    #     Args:
    #         feature1:
    #         feature2:
    #         samples:
    #
    #     Returns:
    #         coverage_map, misbehavior_map
    #         coverage_outer_map, misbehavior_outer_map
    #     """
    #     # TODO Refactor:
    #
    #     # Reshape the data as ndimensional array. But account for the lower and upper bins.
    #     coverage_data = np.zeros(shape=(feature1.num_cells, feature2.num_cells), dtype=int)
    #     misbehaviour_data = np.zeros(shape=(feature1.num_cells, feature2.num_cells), dtype=int)
    #
    #     coverage_outer_data = np.zeros(shape=(feature1.num_cells + 2, feature2.num_cells + 2), dtype=int)
    #     misbehaviour_outer_data = np.zeros(shape=(feature1.num_cells + 2, feature2.num_cells + 2), dtype=int)
    #
    #     for sample in samples:
    #         self.add_sample(sample)
    #
    #
    #     return coverage_data, misbehaviour_data, coverage_outer_data, misbehaviour_outer_data
    #
    # def visualize_probability(self, tags=None, feature_selector=None, sample_selector=None):
    #     """
    #         Visualize the probability of finding a misbehavior in a give cell, computed as the total of misbehavior over
    #         the total samples in each cell. This is defined only for cells that have samples in them. Also store
    #         the probability data so they can be post-processed (e.g., average across run/configuration)
    #     """
    #     # Prepare the data by selecting samples and features
    #
    #     filtered_samples = self.samples
    #     self.logger.debug("All samples: %s", len(filtered_samples))
    #     if sample_selector is not None:
    #         filtered_samples = sample_selector(self.samples)
    #         self.logger.debug("Filtered samples: %s", len(filtered_samples))
    #
    #     filtered_features = self.axes
    #     if feature_selector is not None:
    #         filtered_features = feature_selector(self.axes)
    #
    #     figures = []
    #     # Might be redundant if we store also misbehaviour_maps and coverage_maps
    #     probability_maps = []
    #     # To compute confidence intervals and possibly other metrics on the map
    #     misbehaviour_maps = []
    #     coverage_maps = []
    #
    #     total_samples_in_the_map = filtered_samples
    #
    #     # Create one visualization for each pair of self.axes selected in order
    #     for feature1, feature2 in itertools.combinations(filtered_features, 2):
    #
    #         # Make sure we reset this for each feature combination
    #         filtered_samples = total_samples_in_the_map
    #         # Remove samples that are outliers for this map
    #         if self.drop_outliers:
    #             filtered_samples = drop_outliers_for(feature1, filtered_samples)
    #             filtered_samples = drop_outliers_for(feature2, filtered_samples)
    #
    #         coverage_data, misbehaviour_data, _, _ = self._compute_maps_data(feature1, feature2, filtered_samples)
    #
    #         # figure
    #         fig, ax = plt.subplots(figsize=(8, 8))
    #
    #         cmap = sns.cubehelix_palette(dark=0.1, light=0.9, as_cmap=True)
    #         # Cells have a value between 0.0 and 1.0 since they represent probabilities
    #
    #         # Set the color for the under the limit to be white (0.0) so empty cells are not visualized
    #         # cmap.set_under('0.0')
    #         # Plot NaN in white
    #         cmap.set_bad(color='white')
    #
    #         # Coverage data might be zero, so this produces Nan. We convert that to 0.0
    #         # probability_data = np.nan_to_num(misbehaviour_data / coverage_data)
    #         raw_probability_data = misbehaviour_data / coverage_data
    #
    #         # For some weird reason the data in the heatmap are shown with the first dimension on the y and the
    #         # second on the x. So we transpose
    #         probability_data = np.transpose(raw_probability_data)
    #
    #         sns.heatmap(probability_data, vmin=0.0, vmax=1.0, square=True, cmap=cmap)
    #
    #         xtickslabel = [round(the_bin, 1) for the_bin in feature1.get_bins_labels()]
    #         ytickslabel = [round(the_bin, 1) for the_bin in feature2.get_bins_labels()]
    #         #
    #         ax.set_xticklabels(xtickslabel)
    #         plt.xticks(rotation=45)
    #         ax.set_yticklabels(ytickslabel)
    #         plt.yticks(rotation=0)
    #
    #         tool_name = str(self._get_tool(filtered_samples))
    #         run_id = str(self._get_run_id(filtered_samples)).zfill(3)
    #
    #         title_tokens = ["Mishbehavior Probability", "\n"]
    #         title_tokens.extend(["Tool:", tool_name, "--", "Run ID:", run_id])
    #
    #         if tags is not None and len(tags) > 0:
    #             title_tokens.extend(["\n", "Tags:"])
    #             title_tokens.extend([str(t) for t in tags])
    #
    #         the_title = " ".join(title_tokens)
    #
    #         fig.suptitle(the_title, fontsize=16)
    #
    #         # Plot small values of y below.
    #         # We need this to have the y axis start from zero at the bottom
    #         ax.invert_yaxis()
    #
    #         # axis labels
    #         plt.xlabel(feature1.feature_name)
    #         plt.ylabel(feature2.feature_name)
    #
    #         # Include data to store the file with same prefix
    #
    #         # Add the store_to attribute to the figure and maps object
    #         setattr(fig, "store_to", "-".join(["probability", tool_name, run_id, feature1.feature_name, feature2.feature_name]))
    #         figures.append(fig)
    #
    #         probability_maps.append({
    #             "data": raw_probability_data,
    #             "store_to": "-".join(["probability", tool_name, run_id, feature1.feature_name, feature2.feature_name])
    #         })
    #
    #         misbehaviour_maps.append({
    #                 "data": misbehaviour_data,
    #                 "store_to": "-".join(["misbehaviour", tool_name, run_id, feature1.feature_name, feature2.feature_name])
    #         })
    #
    #         coverage_maps.append({
    #                 "data": coverage_data,
    #                 "store_to": "-".join(["coverage", tool_name, run_id, feature1.feature_name, feature2.feature_name])
    #         })
    #
    #
    #     return figures, probability_maps, misbehaviour_maps, coverage_maps

    def is_cell_free(self, sample):
        # Coordinates reason in terms of bins 1, 2, 3, while data is 0-indexed
        x_coord = self.feature_x.get_coordinate_for(sample) - 1
        y_coord = self.feature_y.get_coordinate_for(sample) - 1

        return self.coverage_data[x_coord, y_coord] == 0

    def add_sample(self, sample):
        # Coordinates reason in terms of bins 1, 2, 3, while data is 0-indexed
        x_coord = self.feature_x.get_coordinate_for(sample) - 1
        y_coord = self.feature_y.get_coordinate_for(sample) - 1

        # Increment the coverage cell
        self.coverage_data[x_coord, y_coord] += 1

    def visualize(self):
        """
            Visualize the current map and the features on a map. The map cells contains the number of samples for each
            cell, so empty cells (0) are white, cells with few elements have a light color, while cells with more
            elements have darker color. This gives an intuition on the distribution of the misbheaviors and the
            collisions

        Args:

        Returns:
            figure
        """

        # Compute data
        #coverage_data, misbehaviour_data, _, _ = self._compute_maps_data(feature1, feature2, self.samples)

        # figure
        figure, ax = plt.subplots(figsize=(8, 8))

        # Set the heatmap
        cmap = sns.cubehelix_palette(dark=0.5, light=0.9, as_cmap=True)
        # Set the color for the under the limit to be white (so they are not visualized)
        cmap.set_under('1.0')

        # For some weird reason the data in the heatmap are shown with the first dimension on the y and the
        # second on the x. So we transpose
        coverage_data = np.transpose(self.coverage_data)

        sns.heatmap(coverage_data, vmin=1, vmax=20, square=True, cmap=cmap)

        xtickslabel = [round(the_bin, 1) for the_bin in self.feature_x.get_bins_labels()]
        ytickslabel = [round(the_bin, 1) for the_bin in self.feature_y.get_bins_labels()]
        #
        ax.set_xticklabels(xtickslabel)
        plt.xticks(rotation=45)
        ax.set_yticklabels(ytickslabel)
        plt.yticks(rotation=0)

        figure.suptitle("Feature Map Coverage", fontsize=16)

        # Plot small values of y below.
        # We need this to have the y axis start from zero at the bottom
        ax.invert_yaxis()

        # axis labels
        plt.xlabel(self.feature_x.feature_name)
        plt.ylabel(self.feature_y.feature_name)

        return figure
