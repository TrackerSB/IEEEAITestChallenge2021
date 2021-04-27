# Deliverable #1

## General approach to testing

### Our experience
Our team did already a range of papers and thesis in the fields of testing autonomous cars in simulations, automatically generating test scenarios for autonomous cars and providing a platform for running those tests.

#### AC3R
\<TODO\>

#### DriveBuild ([see &rArr;](https://www.researchgate.net/publication/341110007_DriveBuild_Automation_of_Simulation-based_Testing_of_Autonomous_Vehicles))
DriveBulid is a platform for:
 - running and distributing simulations testing autonomous cars over a network
 - connecting custom test generators and AIs over a tiny and thus simple interface
 - describing maps and test oracles in a straight forward, easy to understand and yet powerful XML format
 - automatically generating maps based on the XML description
 - collecting varios data for justifying the quality of test generators and AIs in a big data manner

#### Even more papers...
\<TODO\>

### Our approach
\<TODO\>

## Test case 01
\<TODO\>

## Test case 02
\<TODO\>

## Test case 06
The demonstrated approach is about test generation.
In this test generation an abstract scenario is defined at which a pedestrian walks straight over a crosswalk and an autonomous vehicle approaching that crosswalk in a straight line as well.

The interesting point is the fact that we identified multiple aspects about this at first glance easy scenario to modify and tweak the situations one can produce.
So the abstract test case combined with a set of configuration parameters yields a specific test instance.
Such an approach is especially interesting when dealing with other research paper that describe heuristics or search based approaches for tweaking exactly such parameters in order to increase e.g. the criticality of test scenarios.

Concerning this test case the configurable parameters include:
- The test location (i.e. specific locations on any map).
The predefined test locations include multiple crosswalks on the maps San Francisco and CubeTown.
- The speed of the pedestrian
- The approach direction of the pedestrian (i.e. the pedestrian approaches from the left or the right)
- The speed of the ego vehicle
- The distance in which the ego vehicle starts
- If no distance for the ego vehicle is giving the distance is calculated such a way that under the assumption that the vehicle drives at constant speed and Apollo is disabled the pedestrian is hit

Additionally the sets of configuration parameters that describe a certain test instance are checked for plausibility.
This includes that configurations are rejected e.g. if a configuration places a car outside the map.

## Ideas and plans for phase 2
\<TODO\>
