import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionClient
from viam.components.camera import Camera
from viam.components.base import Base


async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='m70v6bcxdkkfgi7b05diwlajs31t66su',
        api_key_id='2942abf3-3248-4d05-b911-c7e5a4ec280b'
    )
    return await RobotClient.at_address("ADDRESS FROM THE VIAM APP", opts)


# Get largest detection box and see if it's center is in the left, center, or
# right third
def leftOrRight(detections, midpoint):
    largest_area = 0
    largest = {"x_max": 0, "x_min": 0, "y_max": 0, "y_min": 0}
    if not detections:
        print("nothing detected :(")
        return -1
    for d in detections:
        a = (d.x_max - d.x_min) * (d.y_max-d.y_min)
        if a > largest_area:
            a = largest_area
            largest = d
    centerX = largest.x_min + largest.x_max/2
    if centerX < midpoint-midpoint/6:
        return 0  # on the left
    if centerX > midpoint+midpoint/6:
        return 2  # on the right
    else:
        return 1  # basically centered


async def main():
    spinNum = 10         # when turning, spin the motor this much
    straightNum = 300    # when going straight, spin motor this much
    numCycles = 200      # run the loop X times
    vel = 500            # go this fast when moving motor

    # Connect to robot client and set up components
    robot = await connect()
    base = Base.from_robot(robot, "my_base")
    camera_name = "<camera-name>"
    camera = Camera.from_robot(robot, camera_name)
    frame = await camera.get_image(mime_type="image/jpeg")

    # Grab the vision service for the detector
    my_detector = VisionClient.from_robot(robot, "my_color_detector")

    # Main loop. Detect the ball, determine if it's on the left or right, and
    # head that way. Repeat this for numCycles
    for i in range(numCycles):
        detections = await my_detector.get_detections_from_camera(camera_name)

        answer = leftOrRight(detections, frame.size[0]/2)
        if answer == 0:
            print("left")
            await base.spin(spinNum, vel)     # CCW is positive
            await base.move_straight(straightNum, vel)
        if answer == 1:
            print("center")
            await base.move_straight(straightNum, vel)
        if answer == 2:
            print("right")
            await base.spin(-spinNum, vel)
        # If nothing is detected, nothing moves

    await robot.close()

if __name__ == "__main__":
    print("Starting up... ")
    asyncio.run(main())
    print("Done.")