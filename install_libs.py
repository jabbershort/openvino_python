import os
import sys
import shutil
import sysconfig
import subprocess


file_names = ['libopenvino_intel_myriad_plugin.so','usb-ma2x8x.mvcmd']
python_version = str(sys.version_info.major)+str(sys.version_info.minor)
print(f"Python version: {python_version}")
libs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),f'build/py{python_version}/wheels')
package_names = os.listdir(libs_path)

for n in package_names:
    if n.startswith("openvino-"):
        wheel_name = n
        break

if not wheel_name:
    exit()

print(subprocess.check_output(f"pip install --upgrade pip",shell=True))
print(subprocess.check_output(f"pip install opencv-python",shell=True))
print(subprocess.check_output(f"pip install {os.path.join(libs_path,wheel_name)}",shell=True))

site_package_folder = sysconfig.get_paths()["purelib"]
destination_path = os.path.join(site_package_folder,'openvino/libs')


for file_name in file_names:
    print(f'Copying {file_name}')
    shutil.copy(
        os.path.join(libs_path,file_name),
        os.path.join(destination_path,file_name)
    )

