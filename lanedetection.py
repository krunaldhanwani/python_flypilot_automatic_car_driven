import cv2
import numpy as np
import asyncio

# Function for lane detection
def detect_lanes(frame):
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

# Function for basic car control
async def control_car(answer, base, spinNum=10, straightNum=300, vel=500):
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

async def main():
    spinNum = 10
    straightNum = 300
    vel = 500

    robot = await connect()  # Replace this with your connection code
    base = Base.from_robot(robot, "base")  # Replace with your robot component

    # Capture video from your camera or use a pre-recorded video
    cap = cv2.VideoCapture("path/to/your/video.mp4")  # Replace with your video source

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Lane detection
        result = detect_lanes(frame)

        # Display the result
        cv2.imshow("Lane Detection", result)

        # Get the lane detection result
        answer = laneDetection(frame)

        # Control the car based on lane detection
        await control_car(answer, base, spinNum, straightNum, vel)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    await robot.close()

if __name__ == "__main__":
    print("Starting up... ")
    asyncio.run(main())
    print("Done.")
