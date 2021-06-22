import os

from lxml import etree
from opendrive2lanelet.opendriveparser import parser as opdParser


def get_junction_info(path: os.path):
    with open(path, 'r') as fh:
        parser = etree.XMLParser()
        rootNode = etree.parse(fh, parser).getroot()

        roadNetwork = opdParser.parse_opendrive(rootNode)

        # Loop through junction info
        for junction in roadNetwork.junctions:
            print(f'Junction ID: {junction._id}')
            connectingRoadSet = set()

            # Get connecting road for each junction
            # A connecting road can be a lane-connector segment INSIDE the intersection
            # The connecting road can also be another road segment
            for connection in junction._connections:

                connectingRoad = roadNetwork.getRoad(connection._connectingRoad)
                connectingRoadSet.add(connectingRoad._id)

            # Get the connecting point of incoming road, outgoing road and connecting road
            # If contact point is "start", get the 1st coordinate (x,y) of incoming/outgoing road
            # If contact point is "end", get the last coordinate (x,y) of incoming/outgoing road
            for connectingRoadId in connectingRoadSet:
                connectingRoad = roadNetwork.getRoad(connectingRoadId)

                predecessor = connectingRoad._link.predecessor
                predecessorRoad = roadNetwork.getRoad(connectingRoad.
                                                      _link.predecessor.element_id)

                incomingRoadConnCoord = predecessorRoad._planView._geometries[0] \
                    if predecessor.contactPoint == 'start' \
                    else predecessorRoad._planView._geometries[-1]

                print('\n\t Connected Roads Pair:')

                successor = connectingRoad._id
                successorRoad = roadNetwork.getRoad(successor)
                outgoingRoadConnCoord = successorRoad._planView._geometries[1]

                if hasattr(connectingRoad._link, "succesor"):
                    successor = connectingRoad._link.successor
                    successorRoad = roadNetwork.getRoad(successor.element_id)

                    outgoingRoadConnCoord = successorRoad._planView._geometries[0] \
                        if successor.contactPoint == 'start' \
                        else successorRoad._planView._geometries[-1]

                print(f'\t\t \
                        \n\t\t incomingRoad: {predecessorRoad._id}, startCoord:{incomingRoadConnCoord._start_position} \
                        \n\t\t outgoingRoad: {successorRoad._id}, startCoord:{outgoingRoadConnCoord._start_position}')
