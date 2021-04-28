# Deliverable #1

## Introduction

This document introduces our team, describes the main goal and approaches while preparing Deliverable 1, and concludes with a summary of our experience with the IEEE AI Testing Challenge so far.

Additionally, as a teaser, we include few ideas for Deliverable 2.
Notably, we will not generate simulations from NHTSA crash reports, as we already published an approach [1] and implemented a tool [2] for doing that, and we feel this might not be entirely novel.

## The Team 

Our team has previous experience in the simulation-based testing domain. We have published several papers on automate generation of tests for self-driving car software (e.g., [1]-[4]) and authored many M. Sc. and B. Sc. theses (e.g., [5]-[7]). A complete list of publications can be found here [8].

We also have organized a challenge similar to the IEEE AI Testing Challenge in the context of the 14th Intl. Workshop on Search-Based Software Testing (SBST). You can read more about our competition on the official web site [9], but the gist of it is that we asked participants to procedurally generate roads. Since the workshop will be held on the 31st of May, you can consider to register for it and join our discussion on how to test those system (and organize challenges for that).

#### Why did we join the IEEE AI Testing Challenge?
Our team joined the competition out of scientific curiosity, to gain more experience with new tools, simulators, and Apollo, and to meet other researchers and practitioners in the domain. We also hope that joining the IEEE AI Testing Challenge might be an effective means to promote our research -- and ourselves -- to a broader audience, potentially leading to establishing fruitful collaborations and research projects.
 

## Main Goal and General Approach to Testing
According to our understanding, the main goal of Deliverable 1 is to prove we familiarized with the technological stack, comprising the simulator, the APIs, and Apollo, and that we can create (automated) and diverse tests.

So in this first period we worked towards this goal. We attended the Q/A sessions, watched videos and read the documentation, tried out the examples, and inspected the source code (to understand the APIs mostly). We installed the required software under different platforms (Ubuntu, Mac, and Windows), and tried to make everything run smoothly. Unfortunately, we managed to have a complete setup (simulator, api, and Apollo) only on our Ubuntu machine. Nevertheless, we are able to generate diverse tests in various scenarios (see the links to the videos), based on the given suggestions and the NHTSA documentation.

Below we report on what we have done, while the links to the YouTube videos and the actual code for the replication of our experiments can be found in the repository.

The general approach that we adopted includes implementing the tests using available python testing frameworks (i.e., `unites`). We started by creating  simple test scenarios that do not involve Apollo, and incrementally, we developed more complex scenarios (that involve Apollo) and increased the automation level from manually written "fixed" tests to parametric tests that enable automated test space exploration. For example, in Test Case 02 we show how to implement a simplistic search process, while in Test Case 06, we show how we defined an abstract scenario and instantiate it in different ways.

The scripts we committed to this repo are meant to exemplify some of the possibilities we explored for creating diverse and effective tests, and show our ability to create scenarios with different initial conditions, testing goals, assertions, environments, and levels of automation. We believe that this result should be enough to convince the jury that we have the means and the skills to move on in the competition.

Finally, while working on Deliverable 1, we identified opportunities to raise the abstraction level of the tests and, consequently, implemented few python modules to help developers (i.e., us) writing better tests more effectively. Of course, given the short time we had, we could not validate our claims empirically.

### Manual Testing

To familiarize with the platform and the simulator we studied different methods to place vehicles and control them during the test execution. Our aim is to ease the generation of different setups (e.g., initial placement, selection of ego/non-ego vehicles) and scenarios (e.g., following lanes, merging lanes, following cars) by providing powerful abstractions.

Using those methods, we successfully provide test cases for placing cars in different positions in a given scenario, e.g., putting the ego car and more than one NPCs on the different and same lane with configurable distance on how many meters counting from the initial point and driving the ego car and NPCs on the scenario with design speeds and different directions. As a result, we can provide a scenario that drives the ego car closely behind the truck by utilizing those design schemes.
Those scenarios are implemented in the scripts under `test_case_01` and 
`test_case_02` folders. Some of those tests can be seen in action in the following videos: [[10]](https://youtu.be/BHEIMy_OqSI), [[11]](https://youtu.be/VOSgbUkh_JQ), [[12]](https://youtu.be/DZtiPGa6Isg)


Test Case 01 and Test Case 02 focus on placing vehicles and moving them, and since they are our first attempt in doing so, these tests take place on a single straight road. Additionally, we configure the ego car to move along a predefined path (i.e., we manually fix the control), to study the effectiveness and reliability of our test oracles. So, to clarify further this point, the goal here is *not* to test Apollo, rather, we create different (yet simple) tests and predictable executions to assess our oracles. In particular, we created both positive [[10]](https://youtu.be/BHEIMy_OqSI) and negative tests [[11]](https://youtu.be/VOSgbUkh_JQ).

### Parameter Exploration

After we familiarized with the simulator and APIs, we increased the level of automation of our tests and implemented a script that explores the parameter of a lane changes scenario. The script repeatedly executes the scenario by changing some parameters (e.g., speed of the ego vehicle, distance between non-ego vehicles) to find the most promising configuration, i.e., it generate a scenario that results in a crash. For the sake of illustration, we do not let Apollo drive in this test.

The script implementing this test case can be found [HERE].
The video is available [HERE] instead.

### Forcing the Initial Conditions on the Ego Car

While working on Deliverable 1, we realized that most of the available tests and examples, assume that the ego and non-ego vehicles are stationary at the beginning of the test. This is a sensible setup to test some aspects of the ego-car, but not all of them. For example, letting the ego-car drive autonomously from the beginning of the test, makes it hard (or even impossible) to test safety-critical situations such as driving to fast in front of a stop sign or a red light, or driving too closely to the heading car. Therefore, we propose and implemented a way to test the ego-car under non-stationary initial conditions.

In essence, our tests connect the required Apollo modules except Control at the beginning of the execution and set a destination point. This way Apollo can start perceiving the environment and planning its trajectory, but cannot move autonomously. Next, the tests control the ego-car and drive it around until the execution conditions match the expected initial conditions of the test (e.g., the ego-car speed is above the speed limit). At this point, the tests enable Apollo control module, so it can drive the ego-car to the destination (while potentially dealing with critical situations).

To illustrate this idea we implemented [SCRIPT XXX]. The video illustrating the script in action is available [HERE].

### Generating Tests From Abstract Scenarios

Test Case 06 is about demonstrating how we can generate concrete tests from abstract scenarios. To do so, we first devised an abstract scenario in which a pedestrian walks straight over a crosswalk and the ego-car approaches that crosswalk. The task for the ego-car is to avoid hitting the pedestrian while passing over the crosswalk.

This abstract scenario can be implemented in many different ways, creating many diverse tests. For example, the pedestrian might cross the road from right to left, or in the opposite direction. Similarly, the pedestrian might or might not move at a constant speed while crossing.

We identified multiple aspects about this scenarios and captured them be means of configurable parameters, and implemented a code that rely on those parameters to instantiate the different (concrete) tests. So the abstract test case combined with the set of configuration parameters yields a specific test instance.

Specifically, we identified the following parameters for the abstract test case at hand:

- Test location, i.e., specific locations on predefined map where the scenario can effectively take place. We provide some predefined test locations on San Francisco and CubeTown maps for the sake of illustration.
- The speed of the pedestrian.
- The approach direction of the pedestrian, i.e., whether the pedestrian approaches the crosswalk from left or right w.r.t. the ego-car direction.
- The target speed of the ego vehicle.
- The distance between the ego-car and the crosswalk. This parameter in combination with the "test location" defines the initial placement of the ego-car.

Our code also check the validity of the provided configuration parameters, for example, it will reject configurations that place the ego-car outside of the road. [@Stefan - Can you elaborate a bit more here?]

Not all the parameters are mandatory, and when some of them are not given, the code compute some "smart" default. For example, if no distance between the  ego-car and the crosswalk is give, the code calculates a distance that ensures the ego-car will hit the pedestrian at a given speed, unless Apollo controls the car. This is an example of how we can effectively generate critical scenarios (e.g., near crash, crash)

Notably, in Deliverable 1, we show only how to "manually" set the parameters to create the concrete tests; however, the aim of this setup is to enable heuristics and search-based approaches that can identify combination of parameters to create, for example, safety-critical situations.

-- Alessio HERE

## Experience Report
Setting up the simulator is ok, Apollo is not trivial at all
Some confusion with the aim of the competition, the main requirements, and its evaluation
Great job for Q/A, provisioning of learning material, but technology is moving fast (need to re-setup the scripts) which makes the setup challenging

## Ideas and plans for phase 2
\<TODO\>

# References
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