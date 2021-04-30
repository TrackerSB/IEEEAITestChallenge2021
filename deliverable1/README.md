# Deliverable #1

## Introduction

This document represents our written simulation test report.

In this document, we introduce our team, describe the main goal and approaches while preparing Deliverable 1, i.e., the generated test scenario scripting methods, and conclude with a summary of our experience with the IEEE AI Testing Challenge so far.

Additionally, as a teaser, we include few ideas for Deliverable 2.
Notably, we will not generate simulations from NHTSA crash reports, as we already published an approach for doing that [1] and implemented in an open-source tool [2]. We feel submitting the same approach for this tool competition might be not entirely fair and novel.

### TL;DR

We implemented several scripts that cover the suggested test cases and experimented with different levels of automation (manual test, parameter exploration, etc.) to generate a diversified set of driving scenarios.  All the tests use standard maps, such as SingleLaneRoad, SanFrancisco, and CubeTown, while the routes are either hardcode in the tests or generated automatically by our scripts.

Despite our previous experience in the domain and the hard work we put into preparing Deliverable 1, we could not run our tests against a fully functional Apollo installation. For example, in our installation, both the Radar and Control modules did not work, so the ego-car cannot perceive pedestrians nor move autonomously. We'll address this issue for Deliverable 2. 

To cope with this situation, we followed the suggestions posted on the Challenge Web site and created "unit tests" instead. Consequently, our scripts rely on `pytest` as the underlying testing framework and generate standard (HTML) reports. Notably, our scripts implement both positive and negative cases, i.e., they drive the ego car to pass and purposely fail the tests to cover both normal and critical scenarios.

For Deliverable 1, we used the `2020.06` version of the simulator and the Python API version in the branch `preview2`.


## The Team 

Our team has previous experience in the simulation-based testing domain. We have published several papers on the automated generation of tests for self-driving car software (e.g., [1]-[4]), implemented several tools, and authored M.Sc. and B.Sc. theses (e.g., [5]-[7]). A complete list of publications can be found here [8].

This year, we also have organized a challenge similar to the IEEE AI Testing Challenge in the context of the 14th Intl. Workshop on Search-Based Software Testing (SBST). You can read more about that competition on the official website [9]. For the SBST tool competition, we asked participants to generate roads procedurally for testing lane-keeping systems. 

> NOTE: Since the workshop will be held on the 31st of May 2021, you can consider registering for it and joining our discussion on testing self-driving cars.

#### Why did we join the IEEE AI Testing Challenge?
Our team joined the competition out of scientific curiosity, to gain more experience with new tools, simulators, and Apollo, and to meet other researchers and practitioners in the domain. We also hope that joining the IEEE AI Testing Challenge might be an effective means to promote our research -- and ourselves -- to a broader audience, which might lead to establishing fruitful collaborations and research projects.

## Main Goal and General Approach to Testing
According to our understanding, the main goal of Deliverable 1 is to prove we have familiarized ourselves with the technological stack (simulator, the APIs, and Apollo) and that we can create various tests, both manually and automatically.

We worked towards this goal during this period and attended the Q/A sessions, watched videos, and read the documentation. We also tried out some of the available examples and inspected the source code published on GitHub to understand the APIs. We installed the required software under different platforms (Ubuntu, Mac --using Parallels, and Windows) and tried to make everything run smoothly. We managed to have a complete setup (simulator, APIs, and Apollo 5.0) with only one Ubuntu machine; however, we could not make Apollo control the ego car or perceive pedestrians. Nevertheless, we generated many scripts to test various scenarios and cover the suggested cases for Deliverable 1. 

Below we report on what we have done and provide links to the YouTube videos that illustrate the scripts in action. The code for replicating our experiments is available in the repository inside the various `test_case_XX` folders, along with a copy of the (HTML) reports generated while running the tests.

> Note: our tests rely on `pytest`, one of the standard unit testing frameworks for python, so our reports follow `pytest`'s format.

### General Approach

The general approach that we adopted includes implementing the tests using available python testing frameworks (i.e., `unites`). We started by creating simple test scenarios that do not involve Apollo. Incrementally, we developed more complex scenarios (that involve Apollo, at least in theory) and increased the automation level from tests with hardcoded parameters to parametric tests that can explore the parameter space automatically. For example, in `test_case _01`, we show how to implement a simplistic search process to create critical scenarios [[13](https://youtu.be/cIlf7DXdoPw)], while in `test_case_06`, we defined an abstract test scenario and instantiated it in various ways to create diverse and critical tests [[20](https://youtu.be/K-sPx8YBPx4)].

Our scripts exemplify some of the possibilities that we explored for creating diverse and effective tests. Those scripts show our ability to create scenarios with different initial conditions, involving different vehicles (static vs dynamic, cars vs trucks vs school-buses), testing goals (assertions), environments, and levels of automation. We believe that this result should be enough to convince the jury that we have the means and the skills to move on in the competition and attempt the submission of Deliverable 2.

Finally, while working on Deliverable 1, we identified opportunities to raise the abstraction level of the test scripts and, consequently, implemented few python modules to help developers writing better tests and doing it more effectively. Of course, given the short time we had, we could not validate our claims empirically.

### Manual Testing

To familiarize ourselves with the platform and the simulator, we studied different methods to place vehicles and control them during the test execution. We aim to ease the generation of different setups (e.g., initial placement, selection of ego/non-ego vehicles) and scenarios (e.g., following lanes, merging lanes, following cars), providing powerful abstractions.

With the help of this code, we successfully provide test cases for placing cars in different initial positions, e.g., putting the ego car and more than one NPCs at configurable distance, placing vehicles on the same lane or on different lanes, and for moving them at a different speed in various directions.

We did not attempt to generate custom maps, so all our tests only use available maps (i.e., SingleLaneRoad, SanFrancisco, and CubeTown).

The following videos illustrate our approach in action:

- Test 01: Changing Lane
    - Safe Changing Lanes Video [[10]](https://youtu.be/BHEIMy_OqSI)
    - Unsafe Changing Lanes Video [[11]](https://youtu.be/VOSgbUkh_JQ)
    - Ego Car responds to School Bus Changing Lane [[18]](https://youtu.be/MSM0H43yGOk)
    - Ego Car responds to Sedan Changing Lane [[19]](https://youtu.be/Fe7yHTPfHgM)

- Test 02: Car/Truck Following [[12]](https://youtu.be/DZtiPGa6Isg)
- 
- Test 04: Encroaching car [[21]](https://youtu.be/Fe7yHTPfHgM)

- Test 05: School Bus [[17]](https://youtu.be/XKGCy5qy4fc)

Test Case 01 and Test Case 02 focus on placing vehicles and moving them, and since they are our first attempt in doing so, these tests take place on a single straight road. Additionally, we configure the ego car to move along a predefined path to study the reliability of our test oracles. So, to clarify further this point, the goal here was *not* to test Apollo; rather, we created different (yet simple) tests that result in predictable outcomes to assess our oracles. We created both positive [[10]](https://youtu.be/BHEIMy_OqSI) and negative tests [[11]](https://youtu.be/VOSgbUkh_JQ).

### Parameter Exploration

After we have familiarized ourselves with the simulator and the APIs, we increased the automation of our tests and implemented a script that explores some parameters of a simple lane changes scenario. The script repeatedly executes the scenario by changing the speed of the ego vehicle and the distance between non-ego vehicles to find the most promising configuration, i.e., the configuration that results in a crash. 

The script implementing this test case is `test_case_01/lane_change.py` and the video illustrating it is available at [https://youtu.be/cIlf7DXdoPw](https://youtu.be/cIlf7DXdoPw).

### Generating Tests From Abstract Scenarios

`test_case_06` [[20]](https://youtu.be/K-sPx8YBPx4) demonstrates how we generated concrete tests cases from an abstract scenario. Our approach was to devise an abstract scenario in which a pedestrian walks straight over a crosswalk while the ego-car approaches that crosswalk. The ego-car's task is to avoid the pedestrian while passing the crosswalk.

Since this abstract scenario can be implemented in many different ways, for example, the pedestrian might cross the road from right to left or in the opposite direction, and may or may not move at a constant speed while crossing, we identified several aspects of this scenario that can be modified and capture them in parameters. By assigning each parameter a value, we can create various concrete tests.  Specifically, we identified the following parameters for the abstract test case at hand:

- Test locations, i.e., specific locations on a map where the scenario can effectively take place. We use some predefined test locations on San Francisco and CubeTown maps for the sake of illustration in our scripts.
- Pedestrian's speed.
- Pedestrians approaching direction, i.e., whether the pedestrian approaches the crosswalk from left or right w.r.t. the ego-car direction.
- Ego vehicle's target speed.
- The distance between the ego-car and the crosswalk. In combination with the "test location," this parameter defines the initial placement of the ego-car.

A configurable test executor implements the general logic that defines the abstract scenario and checks the validity of the provided parameters. At the current stage this validation consists of rejecting a configurations if it places the ego-car outside of the road.

#### Smart Defaults

Notably, not all the parameters are mandatory to create concrete test cases. When some parameters are missing, our code computes "smart" default values. For example, suppose no distance between the ego-car and the crosswalk is given. In that case, our code calculates a distance that ensures the ego-car will hit the pedestrian at a given speed unless a driving agent (e.g., Apollo) avoids that. 

#### Enabling Automation

This example illustrates how we can effectively generate diverse and critical scenarios (e.g., near-crash, crash) by "manually" setting the parameters of the abstract scenario. However, with this design we aim to enable heuristics and search-based approaches that can identify the combination of parameters to create safety-critical situations automatically.

### Forcing the Initial Conditions on the Ego Car

While working on Deliverable 1, we realized that most of the available tests and examples assume that the ego and non-ego vehicles are stationary at the beginning of each test. This setup is sensible to test many behaviors of the ego-car but cannot be used to test all of them. For example, it is hard (or even impossible) to test safety-critical situations like driving too fast in front of a stop sign or driving too close to the heading car without taking the control away from the self-driving software. Therefore, we propose a way to test the ego-car under "non-stationary" initial conditions.

In essence, the idea is to connect and configure the test subject, i.e., Apollo, since the beginning of the execution, but disabling it "Control" model. This way, Apollo can perceive the environment and plan a trajectory, but cannot drive the ego-car. Next, the tests drive the ego-car until the actual execution conditions (e.g., ego-car's speed) match the expected initial conditions of the test (e.g., the ego-car speed is above the speed limit). At this point, the tests release the control and let Apollo drive the ego-car to the destination, effectively testing whether it can deal with critical situations.

To illustrate this idea, we have implemented several scripts but had to disable them (via a special `pytest` annotation), because our Apollo installation is broken. Nevertheless, we wish the jury can try them out on their Apollo installation (by commenting that annotation out). 


## Experience Report

In this section, we briefly summarize our experience with the IEEE AI Testing Challenge so far. We intend to share some observations about the process and the organization to help improve future editions of the event.

In general, setting up the simulator and using the Python APIs was easy enough. However, we struggled to set up Apollo and failed to run it fully. Unfortunately, making the tests working with Apollo seems to be a stringent requirement for this challenge, and we believe this limits the benefits of having a highly portable simulator like (LG)SVL. For the next editions of the challenge, at least for preparing the submission, participants would benefit by having either mocked driving agents or real agents accessible through remote services (i.e., running in the Cloud).

There was some confusion around the which versions of the simulator, API, and Apollo to use. One could have used older/newer versions of Apollo only under some specific conditions, possibly giving up some essential features to implement the tests. Also, releasing a new version of the simulator _during_ the competition did not help in addressing the confusion. Probably, an official, yet fixed and stable, setup would have helped to reduce the effort to start working on the actual tests. 

The organization of the competition is great, and the Q/A sessions and the material have been very helpful. However, there was some confusion about the concrete goals of the challenge and how the evaluation of Deliverables is planned.  We understand that it is challenging to come up with quantifiable criteria to assess the quality of the generated tests and their diversity in general, but having no reference at all might lead to developing solutions that are difficult to compare objectively. Also, it is easy to "get it wrong" and spend weeks developing something that is off-topic.

## Plan for Deliverable 2

In the hope of capturing the intended aim of the challenge, we brainstormed possible ideas to implement for Deliverable 2. We tried to "think out-of-the-box" while remaining pragmatic. Below we summarize two of such ideas.

### Parking Lot Madness
Create scenarios that take place inside parking lots to test features like Tesla's "Smart Summon".
The idea is to check if the ego-car can safely drive from a parking spot to the parking lot's exit despite pedestrians and other vehicles.
Our idea is to generate scenarios by placing the ego-car in different parking spots and controlling the placement and movement of non-ego cars and pedestrians to create various situations.

### Pass or not Pass?
Check the behavior of the ego-car while handling controlled intersections.
The idea is to take any map, find where controlled intersections and traffic lights are, and (automatically) generate scenarios where the car must pass the various controlled intersections.

Concrete tests can be generated by changing which controlled intersection to pass, the direction that ego-car should follow (e.g., turn right, go straight), and directly acting upon the traffic lights (e.g, flashing lights, turn it off).

Alternatively, we can also place the ego car in the middle of those intersections and try to "trap it there" by controlling the traffic lights. This will let us check whether the car can properly free controlled intersections or get stuck in the middle of it.


## References
[1] Alessio Gambi, Tri Huynh, Gordon Fraser, "Generating effective test cases for self-driving cars from police reports," ESEC/SIGSOFT FSE 2019, 257-267

[2] Tri Huynh, Alessio Gambi, Gordon Fraser, "AC3R: automatically reconstructing car crashes from police reports," ICSE (Companion Volume) 2019: 31-34

[3] Alessio Gambi, Marc Müller, Gordon Fraser, "Automatically testing self-driving cars with search-based procedural content generation", ISSTA 2019, 318-328

[4] Alessio Gambi, Marc Müller, Gordon Fraser, "AsFault: testing self-driving car software using search-based procedural content generation," ICSE (Companion Volume) 2019, 27-30

[5] Michael Heine, B.Sc., “Generating Urban-like Scenarios to Spot Fuel-Inefficient Behavior of Autonomous Cars,“ 2020.

[6] Stefan Huber, M.Sc., “DriveBuild: Automation of Simulation-based Testing of Autonomous Vehicles,” 2019,

[7] Tri Huynh, M.Sc., “Automatic Driving Simulation from Vehicle Crash Reports.”, 2018

[8] Dr. Alessio Gambi - CV, contains a list of relevant publications and mentored theses. [https://staff.fim.uni-passau.de/~gambi/attachments/cv.pdf](https://staff.fim.uni-passau.de/~gambi/attachments/cv.pdf)

[9] The First Cyber-physical Systems (CPS) Testing Competition at SBST, [https://sbst21.github.io/tools/](https://sbst21.github.io/tools/)

[10] Safe Changing Lanes Video, [https://youtu.be/BHEIMy_OqSI](https://youtu.be/BHEIMy_OqSI)

[11] Unsafe Changing Lanes Video, [https://youtu.be/VOSgbUkh_JQ](https://youtu.be/VOSgbUkh_JQ)

[12] Truck Following Video, [https://youtu.be/DZtiPGa6Isg](https://youtu.be/DZtiPGa6Isg)

[13] Lane Change Searching Video, [https://youtu.be/cIlf7DXdoPw](https://youtu.be/cIlf7DXdoPw)

[14] Lane Change Searching Class, `test_case_01/lane_change.py`

[15] Driving Ego Car with Apollo, `test_case_01/test_case_01.py#L163`

[16] Driving Ego Car in General, [https://youtu.be/MbU8xZx-Sc8](https://youtu.be/MbU8xZx-Sc8)

[17] Ego Car responds to Parked School Bus, [https://youtu.be/XKGCy5qy4fc](https://youtu.be/XKGCy5qy4fc)

[18] Ego Car responds to School Bus Changing Lane, [https://youtu.be/MSM0H43yGOk](https://youtu.be/MSM0H43yGOk)

[19] Ego Car responds to Sedan Changing Lane, [https://youtu.be/Fe7yHTPfHgM](https://youtu.be/Fe7yHTPfHgM)

[20] Ego Car avoiding and hitting pedestrians, [https://youtu.be/K-sPx8YBPx4](https://youtu.be/K-sPx8YBPx4)

[21] Ego Car responds to Encroaching car, [https://youtu.be/Fe7yHTPfHgM](https://youtu.be/Fe7yHTPfHgM)