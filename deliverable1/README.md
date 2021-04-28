# Deliverable #1

## Introduction

This document introduces our team, describes the main goal and approaches while preparing Deliverable 1, and concludes with a summary of our experience with the IEEE AI Testing Challenge so far.

Additionally, as a teaser, we include few ideas for Deliverable 2.
Notably, we will not generate simulations from NHTSA crash reports, as we already published an approach [1] and implemented a tool [2] for doing that. We feel this might not be entirely novel.

## The Team 

Our team has previous experience in the simulation-based testing domain. We have published several papers on the automated generation of tests for self-driving car software (e.g., [1]-[4]) and authored many M. Sc. and B. Sc. theses (e.g., [5]-[7]). A complete list of publications can be found here [8].

We also have organized a challenge similar to the IEEE AI Testing Challenge in the context of the 14th Intl. Workshop on Search-Based Software Testing (SBST). You can read more about our competition on the official website [9], but the gist of it is that we asked participants to generate roads procedurally for testing a lane-keeping system. Since the workshop will be held on the 31st of May 2021, you can consider registering for it and joining our discussion on testing self-driving cars.

#### Why did we join the IEEE AI Testing Challenge?
Our team joined the competition out of scientific curiosity, to gain more experience with new tools, simulators, and Apollo, and to meet other researchers and practitioners in the domain. We also hope that joining the IEEE AI Testing Challenge might be an effective means to promote our research -- and ourselves -- to a broader audience, potentially leading to establishing fruitful collaborations and research projects.

## Main Goal and General Approach to Testing
According to our understanding, the main goal of Deliverable 1 is to prove we have familiarized ourselves with the technological stack (simulator, the APIs, and Apollo) and that we can create automated and diverse tests.

So in this first period, we worked towards this goal. We attended the Q/A sessions, watched videos and read the documentation, tried out the examples, and inspected the source code (to understand the APIs mostly). We installed the required software under different platforms (Ubuntu, Mac, and Windows) and tried to make everything run smoothly. Unfortunately, we managed to have a complete setup (simulator, APIs, and Apollo) with only one Ubuntu machine. Nevertheless, we generated diverse tests in various scenarios (see the links to the videos) based on the given suggestions and the NHTSA documentation.

Below we report on what we have done. Links to the YouTube videos and the code for replicating our experiments are available in the repository.


The general approach that we adopted includes implementing the tests using available python testing frameworks (i.e., `unites`). We started by creating simple test scenarios that do not involve Apollo. Incrementally, we developed more complex scenarios (that involve Apollo) and increased the automation level from manually written and "fixed" tests to parametric tests that can automatically explore the parameter space. For example, in Test Case 02, we show how to implement a simplistic search process, while in Test Case 06, we show how we defined an abstract scenario and instantiate it in various ways to create diverse tests.

The scripts we committed here are meant to exemplify some of the possibilities we explored for creating diverse and effective tests. Those scripts show our ability to create scenarios with different initial conditions, testing goals, assertions, environments, and levels of automation. We believe that this result should be enough to convince the jury that we have the means and the skills to move on in the competition.

Finally, while working on Deliverable 1, we identified opportunities to raise the abstraction level of the tests and, consequently, implemented few python modules to help developers (i.e., us) writing better tests more effectively. Of course, given the short time we had, we could not validate our claims empirically.

### Manual Testing
To familiarize ourselves with the platform and the simulator, we studied different methods to place vehicles and control them during the test execution. We aim to ease the generation of different setups (e.g., initial placement, selection of ego/non-ego vehicles) and scenarios (e.g., following lanes, merging lanes, following cars), providing powerful abstractions.

With the help of this code, we successfully provide test cases for placing cars in different positions in a given scenario, e.g., putting the ego car and more than one NPCs on the different and same lane with configurable distance on how many meters counting from the initial point and driving the ego car and NPCs on the scenario with design speeds and different directions. We also implemented a scenario in which the ego-car drives closely behind a truck by utilizing those design schemes.

Those scenarios are implemented in the scripts under `test_case_01` and 
`test_case_02` folders. Some of those tests can be seen in action in the following videos: [[10]](https://youtu.be/BHEIMy_OqSI), [[11]](https://youtu.be/VOSgbUkh_JQ), [[12]](https://youtu.be/DZtiPGa6Isg)

Test Case 01 and Test Case 02 focus on placing vehicles and moving them, and since they are our first attempt in doing so, these tests take place on a single straight road. Additionally, we configure the ego car to move along a predefined path to study the reliability of our test oracles. So, to clarify further this point, the goal here is *not* to test Apollo; rather, we create different (yet simple) tests that result in predictable executions to assess our oracles. We created both positive [[10]](https://youtu.be/BHEIMy_OqSI) and negative tests [[11]](https://youtu.be/VOSgbUkh_JQ).

### Parameter Exploration

After we have familiarized ourselves with the simulator and the APIs, we increased the automation of our tests and implemented a script that explores some parameters of a simple lane changes scenario. The script repeatedly executes the scenario by changing the speed of the ego vehicle and the distance between non-ego vehicles to find the most promising configuration, i.e., the configuration that results in a crash. For the sake of illustration, we do not let Apollo drive in this test.

The script implementing this test case can be found [HERE].
The video is available [HERE] instead.

### Forcing the Initial Conditions on the Ego Car

While working on Deliverable 1, we realized that most of the available tests and examples assume that the ego and non-ego vehicles are stationary at the beginning of each test. This setup is sensible to test most of the behaviors of the ego-car but cannot be used to test all of them. For example, it is hard (or even impossible) to test safety-critical situations like driving too fast in front of a stop sign or driving too closely to the heading car without taking the control away from the self-driving software. Therefore, we propose and implement a way to test the ego-car under "non-stationary" initial conditions.

In essence, our tests connect the required Apollo modules except for "Control" at the beginning of the execution and set a destination point. This way, Apollo can start perceiving the environment and planning a trajectory, but the ego-cart cannot move autonomously. Next, the tests control the ego-car and drive it until the execution conditions match the expected initial conditions of the test (e.g., the ego-car speed is above the speed limit). At this point, the tests release the control and let Apollo drive the ego-car to the destination (while potentially dealing with critical situations).

To illustrate this idea, we implemented [SCRIPT XXX]. A video that illustrates this idea is available [HERE].

### Generating Tests From Abstract Scenarios

Test Case 06 is about demonstrating how we can generate concrete tests from abstract scenarios. To do so, we first devised an abstract scenario in which a pedestrian walks straight over a crosswalk and the ego-car approaches that crosswalk. The task for the ego-car is to avoid hitting the pedestrian while passing over the crosswalk.

This abstract scenario can be implemented in many different ways, creating many diverse tests. For example, the pedestrian might cross the road from right to left or in the opposite direction. Similarly, the pedestrian may or may not move at a constant speed while crossing.

We identified several aspects of this scenario that can be modified to create various tests and defined configurable parameters to capture them. We implemented a test executor that relies on those parameters to create different (concrete) tests. So the abstract test case combined with the set of configuration parameters yields a specific test instance.

Specifically, we identified the following parameters for the abstract test case at hand:

- Test locations, i.e., specific locations on a map where the scenario can effectively take place. We use some predefined test locations on San Francisco and CubeTown maps for the sake of illustration in our scripts.
- The speed of the pedestrian.
- The approach direction of the pedestrian, i.e., whether the pedestrian approaches the crosswalk from left or right w.r.t. the ego-car direction.
- The target speed of the ego vehicle.
- The distance between the ego-car and the crosswalk. In combination with the "test location," this parameter defines the initial placement of the ego-car.


Our code also checks the validity of the provided configuration parameters. For example, it rejects configurations that place the ego-car outside of the road. [@Stefan - Can you elaborate a bit more here?]

Notably, not all the parameters are mandatory. When some parameters are not defined, our code computes "smart" default values. For example, suppose no distance between the ego-car and the crosswalk is given. In that case, the code calculates a distance that ensures the ego-car will hit the pedestrian at a given speed unless Apollo avoids that. This example illustrates how we can effectively generate diverse and critical scenarios (e.g., near-crash, crash).

Deliverable 1 shows how "manually" setting these parameters leads to generating diverse concrete tests; however, this setup aims to enable automated heuristics and search-based approaches that can identify the combination of parameters to create safety-critical situations.

## Experience Report
In this section, we briefly summarize our experience with the IEEE AI Testing Challenge so far. We intend to share some observations about the process and the organization to help improve future editions of the event.

In general, setting up the simulator and using the Python APIs was easy enough. However, we struggled to set up Apollo and failed to run on a system other than Ubuntu. Unfortunately, making the tests working with Apollo seems to be a stringent requirement for this challenge, which limits the benefits of having a highly portable simulator like (LG)SVL.

There was quite a lot of confusion around the intended versions of the simulator, API, and Apollo. One could have used older/newer versions of Apollo only under some specific conditions, possibly giving up some essential features to implement the tests (i.e., dreamview API). Also, releasing a new version of the simulator during the competition contributed to increasing the confusion further. Probably, an official setup would have helped to reduce the effort to start working on the tests. Also, the possibility to access some cloud-based resources, e.g., Apollo,  could have helped.

The organization of the competition was great, and the Q/A sessions and the material are very helpful.  However, there was some confusion around the expectations on the deliverables and their evaluation.  We understand that it is challenging to come up with quantifiable criteria to assess the quality of the generated tests and their diversity in general, but having no reference at all might lead to us developing solutions that are difficult to compare objectively.

## Plan for Deliverable 2

In the hope of capturing the intended aim of the competition, we brainstormed possible ideas to implement for Deliverable 2. We tried to "think out-of-the-box" while remaining pragmatic. Below we summarize two of such ideas.


### Parking Lot Madness
Those tests aim to create (or re-create) scenarios that take place inside parking lots to test features like Tesla's "Smart Summon".
The idea is to check if the ego-car can safely drive from a parking spot to the parking lot's exit. 
We plan to generate scenarios by placing the ego-car in different initial parking spots and controlling the placement and movement of non-ego cars and pedestrians to create various situations.

### Pass or not Pass?

Those tests aim to check the behavior of the ego-car passing controlled intersections.
The idea is to take any map, find controlled intersections/traffic lights, and generate scenarios where the car must pass a controlled intersection.
Concrete tests are generated by changing the controlled intersection to pass, the direction that ego-car should follow (e.g., turn right, go straight), and directly acting upon the traffic lights.
Additionally, we can also place the ego car in the middle of intersections and play around with the traffic lights to check whether the car can properly free the intersection or gets stuck in the middle of it.


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