import sys
import signal
import pantilthat as pth
from pid import PIDController
from detect import capture_and_detect
from multiprocessing import Value, Process, Manager

# Minimum and maximum positions for the servos
SERVO_MIN = -90
SERVO_MAX = 90

# Resolution for the pi-camera module
RESOLUTION = (1280, 720)
CENTER = (
   RESOLUTION[0] // 2,
   RESOLUTION[1] // 2
   )

# function to handle keyboard interrupt
def signal_handler(sig, frame):
   print("[INFO] You pressed `ctrl + c`! Exiting...")

   pth.servo_enable(1, False)
   pth.servo_enable(2, False)

   sys.exit()

# Helper function to see if a value is in a specific range
def in_range(val, start, end):
   return (val >= start and val <= end)

# Function to set the pan (right-left) and tilt (up-down) location
def set_servos(pan, tilt):
   signal.signal(signal.SIGINT, signal_handler)

   while True:
      pan_angle = -1 * pan.value
      tilt_angle = tilt.value

      # if the pan angle is within the range, pan
      if in_range(pan_angle, SERVO_MIN, SERVO_MAX):
         pth.pan(pan_angle)

      if in_range(tilt_angle, SERVO_MIN, SERVO_MAX):
         pth.tilt(tilt_angle)

# Closed-loop Proportional Integral Derivative (PID) controller that determines
# how much a value should change given the error and amount of time that has
# passed since the last update.
def pid_process(output, p, i, d, box_coord, origin_coord, action):
   signal.signal(signal.SIGINT, signal_handler)

   p = PIDController(p.value, i.value, d.value)
   p.reset()

   while True:
      error = origin_coord - box_coord.value
      output.value = p.update(error)


def pantilt_process_manager(use_tpu):
   # Enable the servos
   pth.servo_enable(1, True)
   pth.servo_enable(2, True)

   # Main logic loop
   with Manager() as manager:
      #--------------------------------------------------------------
      # Create variables that will be shared by the various processes

      # X and Y value of the bounding box. Type = integer
      center_x = manager.Value('i', 0)
      center_y = manager.Value('i', 0)

      center_x.value = CENTER[0]
      center_y.value = CENTER[1]

      # Pan and tilt values for the camera.  Type = integer
      pan = manager.Value('i', 0)
      tilt = manager.Value('i', 0)

      # PID gains for panning.  Type = float
      pan_p = manager.Value('f', 0.005)
      pan_i = manager.Value('f', 0.01)
      pan_d = manager.Value('f', 0)

      # PID gains for tilting.  Type = float
      tilt_p = manager.Value('f', 0.075)
      tilt_i = manager.Value('f', 0.01)
      tilt_d = manager.Value('f', 0)

      # --------------------------------------------------------
      # Create the processes that will run the various functions

      # Graphics process, includes the CNN
      detect_process = Process(target=capture_and_detect, args=(center_x, center_y, use_tpu))

      # Process for panning (move right-left)
      pan_process = Process(target=pid_process, args=(pan, pan_p, pan_i, pan_d, center_x, CENTER[0], 'pan'))

      # Process for tilting (move up-down)
      tilt_process = Process(target=pid_process, args=(tilt, tilt_p, tilt_i, tilt_d, center_y, CENTER[1], 'tilt'))

      # Process for moving servos
      servo_process = Process(target=set_servos, args=(pan, tilt))

      #--------------------
      # Start all processes
      detect_process.start()
      pan_process.start()
      tilt_process.start()
      servo_process.start()

      #-------------------
      # Join all processes
      detect_process.join()
      pan_process.join()
      tilt_process.join()
      servo_process.join()

if __name__ == '__main__':
   pantilt_process_manager()
