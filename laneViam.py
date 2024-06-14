import asyncio
import cv2
import numpy as np

from viam.robot.client import RobotClient
from viam.services.vision import VisionClient
from viam.components.camera import Camera
from viam.components.base import Base

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='m70v6bcxdkkfgi7b05diwlajs31t66su',
        api_key_id='2942abf3-3248-4d05-b911-c7e5a4ec280b'
    )
    return await RobotClient.at_address("mehul-main.zfkpmoz0ju.viam.cloud", opts)

async def detect_lanes(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and help with edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Create a region of interest (ROI) mask
    height, width = edges.shape
    mask = np.zeros_like(edges)
    region_of_interest_vertices = [
        (0, height),
        (width / 2, height / 2),
        (width, height)
    ]
    cv2.fillPoly(mask, [np.array(region_of_interest_vertices, np.int32)], 255)

    # Apply the mask to the edges
    masked_edges = cv2.bitwise_and(edges, mask)

    # Use HoughLinesP to detect lines in the image
    lines = cv2.HoughLinesP(masked_edges, 1, np.pi / 180, 50, minLineLength=100, maxLineGap=50)

    # Draw lines on the original frame
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 5)

    # Combine the line image with the original frame
    result = cv2.addWeighted(frame, 0.8, line_image, 1, 0)

    return result

async def main():
    spinNum = 10
    straightNum = 300
    vel = 500

    robot = await connect()
    base = Base.from_robot(robot, "base")
    camera_name = "camera"
    camera = Camera.from_robot(robot, camera_name)

    for _ in range(200):  # Run for a fixed number of cycles (adjust as needed)
        frame = await camera.get_image(mime_type="image/jpeg")

        # Detect lanes
        result = await detect_lanes(frame)

        # Display the result
        cv2.imshow("Lane Detection", result)

        # Get the lane detection result
        answer = detect_lane(frame)

        # Control the car based on lane detection
        await control_car(base, answer, spinNum, straightNum, vel)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    await robot.close()
    cv2.destroyAllWindows()

async def control_car(base, answer, spinNum=10, straightNum=300, vel=500):
    if answer == 0:
        print("Turn left")
        await base.spin(spinNum, vel)
        await base.move_straight(straightNum, vel)
    elif answer == 1:
        print("Go straight")
        await base.move_straight(straightNum, vel)
    elif answer == 2:
        print("Turn right")
        await base.spin(-spinNum, vel)

def detect_lane(frame):
    # Implement your logic to determine the lane based on the frame
    # This can be a more sophisticated algorithm based on your requirements
    # Return the detected lane (0 for left, 1 for center, 2 for right in this example)
    return 1

if __name__ == "__main__":
    print("Starting up... ")
    asyncio.run(main())
    print("Done.")
