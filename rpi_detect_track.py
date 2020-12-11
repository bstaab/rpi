import sys
import argparse
from manager import pantilt_process_manager
from hardware_test import pantilt_test, camera_test

def camera():
    return camera_test(0)

def pantilt():
   return pantilt_test()

def parse_args():
   parser = argparse.ArgumentParser()
   parser.add_argument('--test', required=False, help='Test mode, valid values are pantilt or camera')
   parser.add_argument('--tpu', action='store_true', help='Use TPU for inference')
   return parser.parse_args()

def main():
   args = parse_args()
   if args.test == 'camera':
      camera()
   elif args.test == 'pantilt':
      pantilt()
   else:
      pantilt_process_manager(args.tpu)

if __name__ == "__main__":
    main()
