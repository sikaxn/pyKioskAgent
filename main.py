import subprocess
import re
from flask import Flask, request, jsonify
import psutil
import platform
import threading
import time
import os
import urllib.request

app = Flask(__name__)

def get_net_info():
    output = subprocess.check_output(['ipconfig', '/all']).decode('utf-8')
    output = output.split('\n')
    devices = []
    device = {}
    for line in output:
        if line.startswith('   '):
            if 'Physical Address' in line:
                mac = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", line)
                if mac:
                    device['mac_address'] = mac.group(0)
                else:
                    device['mac_address'] = 'Not Found'
            elif 'IPv4 Address' in line:
                ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
                if ip:
                    device['ip_address'] = ip[0]
                else:
                    device['ip_address'] = 'Not Found'
        elif line.startswith('\n') or line.startswith('   DNS Servers'):
            continue
        else:
            if device:
                devices.append(device)
            device = {'name': line.strip(), 'mac_address': 'Not Found', 'ip_address': 'Not Found'}
    if device:
        devices.append(device)
    return devices

@app.route('/netinfo')
def net_info():
    net = get_net_info()
    return jsonify(net)
	
@app.route('/deviceinfo')
def device_info():
    cpu = get_cpu_info()
    display = get_display_info()
    memory = get_memory_info()
    disks = get_disk_info()
    return jsonify({
        "cpu": cpu,
        "display": display,
        "memory": memory,
        "disks": disks
    })
	

@app.route('/powermgmt')
def powermgmt():
    method = request.args.get('method')
    time = request.args.get('time')

    # If method is missing or not recognized, return failure
    if not method or method not in ['signoff', 'shutdown', 'restart', 'cancel']:
        return jsonify({'success': False, 'error': 'Missing or invalid method parameter'})

    # If cancel method is requested, execute the shutdown -a command
    if method == 'cancel':
        cmd = 'shutdown /a'
        result = subprocess.run(cmd, shell=True, capture_output=True)

        # Return success or failure based on the exit code of the command
        if result.returncode == 0:
            return jsonify({'success': True, 'method': method})
        else:
            return jsonify({'success': False, 'error': result.stderr.decode()})

    # If time is missing or not an integer, set it to 10 seconds
    try:
        time = int(time) if time else 10
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid time parameter'})

    # If time is less than 10 seconds, treat as success but set it to 10 seconds
    if time < 10:
        time = 10
        return jsonify({'success': True, 'method': method, 'time': time})

    # Construct and execute the command string
    if method == 'signoff':
        cmd = 'shutdown /l /f'
    elif method == 'shutdown':
        cmd = f'shutdown /s /t {time}'
    elif method == 'restart':
        cmd = f'shutdown /r /t {time}'
    else:
        return jsonify({'success': False, 'error': 'Unexpected error'})

    result = subprocess.run(cmd, shell=True, capture_output=True)

    # Return success or failure based on the exit code of the command
    if result.returncode == 0:
        return jsonify({'success': True, 'method': method, 'time': time})
    else:
        return jsonify({'success': False, 'error': result.stderr.decode()})


def run_command(command, timeout):
    # Create a subprocess and start the command
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # Use a thread to read the output of the command in the background
    def read_output():
        while True:
            line = proc.stdout.readline()
            if line == '':
                break
            print(line.rstrip())

    output = ''
    t = threading.Thread(target=read_output)
    t.start()

    # Wait for the command to complete or the timeout to expire
    t.join(timeout)
    if t.is_alive():
        # Timeout expired, kill the process and return an error message
        proc.kill()
        return 'Waited too long for output'

    # Command completed, return the output
    return output

@app.route('/runshell')
def run_shell():
    # Get the method and shellcmd parameters from the query string
    method = request.args.get('method')
    shellcmd = request.args.get('shellcmd')

    # Choose the appropriate shell command based on the method parameter
    if method == 'cmd':
        shell = 'cmd.exe'
        arg = '/c'
    elif method == 'powershell':
        shell = 'powershell.exe'
        arg = '-Command'
    elif method == 'python':
        shell = 'python'
        arg = '-c'
    else:
        return jsonify({'error': 'Invalid method'})

    # Execute the shell command with a timeout of 5 seconds and return the output or an error message
    try:
        output = run_command([shell, arg, shellcmd], timeout=5)
        return jsonify({'method': method, 'shell': shell, 'output': output})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output})

@app.route('/printer')
def printer():
    method = request.args.get('method')
    text = request.args.get('text')
    
    if method == 'print':
        filename = 'WLSDFKJN.DRY'
        with open(filename, 'w') as f:
            f.write(text)
        time.sleep(3)
        if os.path.exists(filename):
            if is_aprint6_running():
                return jsonify({'result': 'print failed', 'text': text})
            else:
                return jsonify({'result': 'not running', 'text': text})
        else:
            return jsonify({'result': 'success', 'text': text})
    
    elif method == 'startagent':
        if is_aprint6_running():
            return jsonify({'result': 'restart'})
        elif start_aprint6():
            return jsonify({'result': 'start'})
        else:
            return jsonify({'result': 'failed to start agent'})
    
    else:
        return jsonify({'result': 'invalid method'})

def is_aprint6_running():
    output = subprocess.check_output('tasklist /FI "IMAGENAME eq APRINT6.EXE"', shell=True)
    return 'APRINT6.EXE' in output.decode()

def start_aprint6():
    # Check for existing instances of APRINT6.EXE and kill them
    subprocess.call('taskkill /F /IM APRINT6.EXE', shell=True)
    time.sleep(1)
    # Start APRINT6.EXE minimized
    try:
        subprocess.Popen(['APRINT6.EXE', '/MIN'])
        return True
    except OSError:
        return False
		
		

@app.route('/download')
def download():
    url = request.args.get('url')
    name = request.args.get('name')
    dir = request.args.get('dir')
    exe = request.args.get('exe')

    # If dir is not given, use the default directory
    if not dir:
        dir = os.path.join(os.environ['TEMP'], 'kioskagent')

    # Check if the directory exists before attempting to download the file
    if not os.path.isdir(dir):
        return jsonify({'status': 'error', 'message': f'Directory {dir} does not exist'})

    # Download the file
    try:
        response = urllib.request.urlopen(url)
        content = response.read()
        if name:
            filename = os.path.join(dir, name)
        else:
            filename = os.path.join(dir, os.path.basename(url))
        with open(filename, 'wb') as f:
            f.write(content)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error downloading file: {str(e)}'})

    # Execute the file if exe is true
    if exe and name and name.lower().endswith(('.exe', '.bat', '.ps1', '.vbs')):
        try:
            if name.lower().endswith('.exe'):
                subprocess.Popen(filename, shell=True)
            elif name.lower().endswith(('.bat', '.ps1')):
                subprocess.Popen(['cmd.exe', '/c', filename], shell=True)
            elif name.lower().endswith('.vbs'):
                subprocess.Popen(['cscript.exe', filename], shell=True)
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error executing file: {str(e)}'})

    # Return the result as a JSON object
    return jsonify({'status': 'success', 'original_file_location': url, 'new_file_location': filename, 'run': exe})

@app.route('/')
def index():
    return 'agent good'

@app.route('/<path:path>')
def invalid(path):
    return 'invalid'

def get_memory_info():
    meminfo = psutil.virtual_memory()
    available = meminfo.available/1024/1024
    total = meminfo.total/1024/1024
    return f"{available:.2f} MB available, {total:.2f} MB total"

def get_disk_info():
    disks = []
    for disk in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(disk.mountpoint)
        except PermissionError as e:
            # Disk is not ready or accessible, skip it
            print(f"Failed to get usage information for {disk.mountpoint}: {e}")
            continue
        disks.append({
            "device": disk.device,
            "mountpoint": disk.mountpoint,
            "filesystem": disk.fstype,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        })
    return disks
	
def get_display_info():
    display_info = []
    try:
        for screen in range(0, 10):
            res = platform.libc.xrandr.XRRGetScreenInfo(platform.display, platform.libc.XDefaultRootWindow(platform.display))
            width = platform.libc.XRRGetScreenSizeRange(platform.display, screen)[1]
            height = platform.libc.XRRGetScreenSizeRange(platform.display, screen)[3]
            rate = platform.libc.XRRConfigCurrentRate(res)
            display_info.append(f"{width}x{height}@{rate}")
    except:
        display_info.append("unknown")
    return ", ".join(display_info)
	
def get_cpu_info():
    cpuname = platform.processor()
    cores = psutil.cpu_count(logical=False)
    freq = psutil.cpu_freq().current
    return f"{cpuname}, {cores} cores, {freq:.2f} MHz"
	
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1')
