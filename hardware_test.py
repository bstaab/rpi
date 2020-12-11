import math
import time
import pantilthat
from picamera import PiCamera

def camera_test(rotation):
   camera = PiCamera()
   camera.rotation = rotation
   camera.start_preview()

   try:
      while True:
         time.sleep(0.250)
         continue
   except KeyboardInterrupt:
      camera.stop_preview()

def pantilt_test():
   while True:
      # Get the time in seconds
      t = time.time()

      # G enerate an angle using a sine wave (-1 to 1) multiplied by 90 (-90 to 90)
      a = int(math.sin(t * 2) * 90)
      pantilthat.pan(a)
      pantilthat.tilt(a)

      # Sleep for a bit so we're not hammering the HAT with updates
      time.sleep(0.005)

if __name__ == '__main__':
   pantilt_test()
