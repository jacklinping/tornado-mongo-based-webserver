import os,sys

root_path = [os.path.dirname( #live-server
        os.path.dirname(
            os.path.abspath(__file__)
            )
       )]
print root_path
sys.path += root_path
