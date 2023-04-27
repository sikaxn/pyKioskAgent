# Kiosk Agent 

## /

make a GET request to the `/`, it will return agent good.

## /netinfo 

make a GET request to the `/netinfo` endpoint to retrieve the network interface information. The response will be a JSON object containing the IP address, MAC address, and name of each network interface.


### Example Output

Here is an example of the JSON output returned by the API:

```json
{
    "Ethernet adapter Ethernet": {
        "ip": "10.0.0.12",
        "mac": "00-50-56-C0-00-FF",
        "name": "Ethernet adapter Ethernet"
    },
    "Ethernet adapter VMware Network Adapter VMnet1": {
        "ip": "192.168.44.1",
        "mac": "00-FF-FF-C0-00-01",
        "name": "Ethernet adapter VMware Network Adapter VMnet1"
    },
    "Ethernet adapter VMware Network Adapter VMnet8": {
        "ip": "192.168.146.1",
        "mac": "00-50-FF-FF-FF-FF",
        "name": "Ethernet adapter VMware Network Adapter VMnet8"
    }
}
```

## /deviceinfo

make a GET request to the `/deviceinfo` endpoint to retrieves system information such as CPU, memory, disk usage, and display information and returns it in JSON format when the `/deviceinfo` endpoint is accessed.

### Example Output

Here is an example of the JSON output returned by the API:

```json
{
  "cpu": "Intel64 Family 6 Model 141 Stepping 1, GenuineIntel, 8 cores, 2304.00 MHz",
  "disks": [
    {
      "device": "C:\\",
      "filesystem": "NTFS",
      "free": 883105722368,
      "mountpoint": "C:\\",
      "percent": 13.7,
      "total": 1023529226240,
      "used": 140423503872
    }
  ],
  "display": "unknown",
  "memory": "25725.51 MB available, 32344.81 MB total"
}

```

## /runshell

The Shell Command API allows you to execute shell commands on your system using a simple HTTP interface. You can use this API to automate system administration tasks, execute shell scripts remotely, and more.

## Usage

To use the Shell Command API, send a GET request to the `/runshell` endpoint with two query parameters: `method` and `shellcmd`.

### Parameters

- `method`: The method to use to execute the shell command. Valid values are `cmd`, `powershell`, and `python`.
- `shellcmd`: The shell command to execute.

### Example

Here's an example of how to use the Shell Command API to execute a shell command using PowerShell:

```
http://localhost:5000/runshell?method=python&shellcmd=print(%27Hello%2C%20world%21%27)
```

This will execute the `Get-ChildItem` command in PowerShell and return the output as JSON.

### Example Output

Here is an example of the JSON output returned by the API:

```json
{
  "method": "python",
  "output": "Hello World",
  "shell": "python"
}
```