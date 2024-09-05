import sys, pathlib, os

if __name__ == "__main__":
    sys.path.append(os.path.join(pathlib.Path(__file__).parent.absolute(), 'Hospital_STT'))
    Hospital_STT = __import__('stt')
    Hospital_STT.SR_Hospital()