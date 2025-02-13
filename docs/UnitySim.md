Quick Links: [Overview & Installation](./README.md) | [Environment](./TanksWorldData.md) | [Evaluation](./Evaluation.md) | [Submission](./Submission.md) 

## Underlying Unity Simulation

### NOTE: This document is about the underlying unity simulation and not the TanksWorld environment python interface.  For documentation about the TanksWorld python environment see: [TanksWorld Data Documentation](./TanksWorldData.md)

## Inputs

### Vector action

float array of length 3; each value has a range range of `[-1,  1]`:

1. forward/backward acceleration
2. angular left/right acceleration
3. shoot/don't shoot ( >0.5 is shoot, <= 0.5 is no-op)

Note that out-of-range values are allowed, but will be internally clamped to the `[-1, 1]` range.

### Decision Interval

The decision interval for the tanks is every 6 steps. This means a learner can only choose an action every 6 steps, and for the steps between decisions, the last known action is applied each time. If a decision is to turn left, it will continue turning left for the next 6 steps. 

The vector observation is sent every 6 steps too. Between decisions, nothing new is sent.

### Reset parameters

None for now!

## Outputs

### Vector Observation

float array of length 84

Every agent reads and returns the exact same observation: truth data about all active tanks.

The observation consists of the states of 12 tanks (5 red, 5 blues, 2 neutral) one after the other. The state of one tank is a float array of length 7.

In order, the states describe red tanks 1-5, blue tanks 1-5, neutral tank 1, neutral tank 2.

The state of one tank looks like this:

0. position x, (appx `[-45, 45]`) 
1. position y, (appx `[-45, 45]`)
2. rotation degrees, `[0, 360)`; 0 is facing towards +z direction; 90 is facing in the +x direction; increases clockwise.
3. My HP `[100, 0]`
4. Whether I killed someone this frame (1 for yes, 0 for no kills)
5. how much damage I dealt to anyone/anything this frame, `[0, 100]`
6. the team of the thing I hit this frame (0 for no hits occured, 1 for team 1 (red), 2 for team 2 (blue), 3 for a neural bystander tank (uh oh!))

e.g. the state of a given tank at the start of the game might look like `[30, 20, 180, 100, 0, 0, 0]`

and the complete observation would be twelve of those, one after the other, in an array of 84 total floats.

### Visual Observation

- one FPV at 84x84 px RGB, unique per agent
- one Minimap view at 128x128 px RGB, which is identical for all agents. It represents the coverage of static obstacles in the scene, including the bounding walls. 
For any pixel that is white in the observation, the corresponding location in the scene will have some obstacle there, e.g. palm tree. 
Black pixels indicate that there is no static obstacle at that spot.
	- This view ignores all tanks.

### Game window

The executable brings up a game window during training with multiple views. 

- Top row: These are the FPVs for the red team, left to right tank 1 through 5. When a tank dies, the FPV stops updating and is crossed out with an X of the tank's team color.
- Second row: All FPVs for the Blue team.
- Bottom right: A cinematic view of the competition; the camera automatically positions itself to capture all alive tanks.
- Bottom left: A minimap-like view of the competition. This view imitates the minimap that the agents receive, but is not actually involved in training and is just for debugging/presentation purposes.
Red triangles indicate red team; Blue triangles are Blue team; Green triangles are bystander tanks. The little circles represent active shells in the scene, and are colored according to the team color of the tank which launched it.

A scoreboard appears over the cinematic view. It depicts the number of friendly, enemy, and collateral kills that each team has collectively performed. On the left is Red's scores, and Blue's are on the right.

## Physics overview

Both the tanks and the launched shells are represented by non-kinematic Rigidbodies in Unity's physics system. The bystander tanks are kinematic rigidbodies - a necessary feature of NavMesh controlled actors. 

Collisions can occur between any rigidbody and any collider. 
Each tank, and every obstacle, has a collider on it that's roughly the size of the object.
When a shell collides with any collider, whether that's another tank or a stationary object, it will detonate. 
Every object with a collider within 5 meters of the shell will take damage proportional to the distance from the explosion. 
Any tank can take damage; stationary objects do not take damage.

Shells always launch at 50 m/s from the front of the tank. They follow an arc through the air and reach a max height of 1.79 meters, and the maximum uninterrupted distance it can achieve is 40.6 meters, almost half the length of the arena. 

Tanks can move at a maximum of 20 m/s forward or backward. If a shell explosion occurs near a tank, it can be pushed away by the explosion force and for the duration its inputs will have no effect. 

### Object dimensions

All dimensions are in length/width/height format, or front-back, left-right, bottom-top size. All in meters. Dimensions are based on the object's collider used for physics interactions, not necessarily the visible mesh.


object | length | width | height
-------|--------|------|-------
Tank   | 1.5     | 1.6   | 1.7
Shell | 0.55|0.3|0.3
Rock|3.33|4.74 | 3.5
Cacti | 2.78 | 2.78 | 2.73
Palm Tree (trunk only) | 1.0 | 1.0 | 4.0
Wall | 3.0 | 1.0 | 3.0
Bunker | 7.13 | 4.15 | 2.84

## Human runtime interactions

Plug in a game controller while running the environment in inference mode to override Red Tank 1's inputs with controller inputs. The controller is successfully detected when the top-left FPV is surrounded in a red border and a "PLAYER 1" label appears at the top of the view. 

To relinquish control back to the policy, unplug the controller.

### Controls

* Move forward: right trigger
* Move backward: left trigger
* Turn left/right: move left thumbstick left or right
* Shoot: press "A" on an XBOX-like controller.

### Debug

If the controller is not detected, try unplugging and re-plugging it in while running the environment so Unity can detect the hardware change. Ensure that it is running in inference mode - the controller will not override while in training mode.

The above controls are tested with a Logitech Gamepad F310. If you are using a different kind of controller or joystick, try out other inputs (bumpers, directional pad, X/Y/B buttons). 