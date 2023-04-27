# Kiosk Agent 

## /

make a GET request to the `/`, it will return ```agent good```.

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

## /download

This command downloads a file from a specified URL and saves it to a specified directory, with an optional filename. If the file is an executable and the `exe` parameter is set to `true`, the file will be executed after it is downloaded.


### Parameters

#### `url` (required)

The URL of the file to be downloaded. This can be a HTTP link, a file from local disk, or an SMB volume.

#### `dir` (optional)

The directory where the downloaded file will be saved. If not provided, the file will be saved to `%TEMP%/kioskagent/`.

#### `name` (optional)

The name of the downloaded file. If not provided, the name of the file from the URL will be used.

#### `exe` (optional)

Whether or not to execute the downloaded file if it is an executable. Set to `true` or `false`. If set to `true` and the filename ends with `.exe`, `.bat`, `.ps1`, or `.vbs`, the file will be executed after it is downloaded.

### Responses

#### Success Response

If the file is downloaded and, if applicable, executed successfully, the endpoint will return a JSON object with a status of `success`, the original file location, the new file location, and whether or not the file was executed:

```
{
    "status": "success",
    "original_file_location": "<url>",
    "new_file_location": "<directory>/<filename>",
    "run": <boolean>
}
```

#### Error Response

If an error occurs during the download or execution process, the endpoint will return a JSON object with a status of `error` and an error message:

```
{
    "status": "error",
    "message": "<error_message>"
}
```

Possible error messages include:

- `Directory <directory> does not exist`: The specified directory does not exist.
- `Error downloading file: <error_message>`: An error occurred while attempting to download the file.
- `Error executing file: <error_message>`: An error occurred while attempting to execute the file.

## /printer

This API for Printer provides two methods for interacting with a printer:

- `print`: saves text as WLSDFKJN.DRY under the same directory of the script, waits for 3 seconds, and returns a JSON response indicating the result of the print operation and the original text being printed.
- `startagent`: checks if APRINT6.EXE is running, and if it is, kills it and starts it minimized. If it's not running, starts it minimized. Returns a JSON response indicating whether the agent was restarted or started.


### `print` Method

To print a text, send a GET request to `/printer` with the following query parameters:

- `method`: The method to use, which should be set to `print`.
- `text`: The text to print.

For example, to print the text "Hello, world!" send a GET request to:

```
http://localhost:5000/printer?method=print&text=Hello%2C%20world%21
```

Note that the text should be URL encoded.

The API will respond with a JSON object with the following keys:

- `result`: The result of the print operation, which can be one of the following:
    - `success`: The text was successfully printed.
    - `print failed`: The text failed to print because APRINT6.EXE is running.
    - `not running`: The text failed to print because APRINT6.EXE is not running.
- `text`: The original text that was printed.

### `startagent` Method

To start or restart the APRINT6.EXE agent, send a GET request to `/printer` with the following query parameters:

- `method`: The method to use, which should be set to `startagent`.

For example, to start the agent, send a GET request to:

```
http://localhost:5000/printer?method=startagent
```

The API will respond with a JSON object with the following keys:

- `result`: The result of the agent start operation, which can be one of the following:
    - `restart`: The agent was restarted because it was already running.
    - `start`: The agent was started because it was not running.
    - `failed to start agent`: The agent failed to start.
    
### Response Headers

The API includes the `Access-Control-Allow-Origin` header in the response, with a value of `*`, allowing any domain to make requests to the API.

### Error Handling

If an invalid method is specified in the request, the API will respond with a JSON object with the following key:

- `result`: The result of the request, which will be `invalid method`.

If the APRINT6.EXE agent fails to start for any reason, the `startagent` method will respond with a JSON object with the following key:

- `result`: The result of the agent start operation, which will be `failed to start agent`.
