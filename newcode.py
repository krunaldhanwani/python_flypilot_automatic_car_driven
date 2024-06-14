import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionClient
from viam.components.camera import Camera
from viam.components.base import Base

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='<API-KEY>',
        api_key_id='<API-KEY-ID>'
    )
    return await RobotClient.at_address("ADDRESS FROM THE VIAM APP", opts)

# Replace this function with an actual lane detection algorithm
def laneDetection(frame):
    # Example: Assume lane is on the left if the left side is brighter than the right side
    left_brightness = sum(frame.crop((0, 0, frame.size[0]//2, frame.size[1])).convert("L").getdata())
    right_brightness = sum(frame.crop((frame.size[0]//2, 0, frame.size[0], frame.size[1])).convert("L").getdata())
    
    if left_brightness > right_brightness:
        return 0  # on the left
    elif left_brightness < right_brightness:
        return 2  # on the right
    else:
        return 1  # center

async def main():
    spinNum = 10
    straightNum = 300
    numCycles = 200
    vel = 500

    robot = await connect()
    base = Base.from_robot(robot, "my_base")
    camera_name = "<camera-name>"
    camera = Camera.from_robot(robot, camera_name)
    
    for i in range(numCycles):
        frame = await camera.get_image(mime_type="image/jpeg")
        answer = laneDetection(frame)
        if answer == 0:
            print("left")
            await base.spin(spinNum, vel)
            await base.move_straight(straightNum, vel)
        elif answer == 1:
            print("center")
            await base.move_straight(straightNum, vel)
        elif answer == 2:
            print("right")
            await base.spin(-spinNum, vel)

    await robot.close()

if __name__ == "__main__":
    print("Starting up... ")
    asyncio.run(main())
    print("Done.")
