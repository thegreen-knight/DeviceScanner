import subprocess
import sys
from segno import helpers
import random
import string
import time
import pyshark
import click

# Function to start the WiFi Hotspot
def startHotspot(CON_NAME, password):
    print(f"Starting Hotspot with Name: {CON_NAME}")

    # Add the WiFi connection
    subprocess.run(["nmcli", "con", "add", "type", "wifi", "ifname", "wlx9cefd5faec45", "con-name", CON_NAME, "ssid", CON_NAME])

    # Modify connection settings
    subprocess.run(["nmcli", "con", "modify", CON_NAME, "802-11-wireless.mode", "ap", "802-11-wireless.band", "bg", "ipv4.method", "shared"])
    subprocess.run(["nmcli", "con", "modify", CON_NAME, "802-11-wireless.channel", "6"])
    if password != "none":
        subprocess.run(["nmcli", "con", "modify", CON_NAME, "wifi-sec.key-mgmt", "wpa-psk"])
        subprocess.run(["nmcli", "con", "modify", CON_NAME, "wifi-sec.psk", password])

    # Bring up the connection
    subprocess.run(["nmcli", "con", "up", CON_NAME])

# Function to generate a random password
def generate_password():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(8))
    return password

# Function to randomly pick a WiFi name
def wifiName():
    names = ['zulu45', 'skynet', 'hunter']
    return random.choice(names)

# Function to extract outgoing connections from captured packets
def extract_outgoing_connections(pkt):
    # Open the file in append mode using 'with' to ensure proper file closure
    with open("data.txt", "a") as collectedData:
        try:
            # Check if packet has IP and TCP layers
            if hasattr(pkt, 'ip') and hasattr(pkt, 'tcp'):
                IpInfo = f"{pkt.ip.dst}:{pkt.tcp.dstport}"
                collectedData.write(IpInfo + '\n')

            # Check if packet has DNS layer
            if hasattr(pkt, 'dns') and hasattr(pkt.dns, 'qry_name'):
                domainname = pkt.dns.qry_name
                collectedData.write(domainname + '\n')

        except AttributeError as e:
            # Handle cases where expected attributes don't exist in the packet
            print(f"Error processing packet: {e}")


# Function to capture traffic on a specific interface
def captureTraffic():
    interface = 'wlx9cefd5faec45'  # Replace with your network interface
    capture = pyshark.LiveCapture(interface=interface)

    # Set the duration for capturing traffic (30 minutes)
    capture_duration = 10 * 60  # 30 minutes in seconds

    # Record the start time
    start_time = time.time()

    for pkt in capture:
        extract_outgoing_connections(pkt)

        # Check if the capture duration has elapsed
        current_time = time.time()
        if current_time - start_time >= capture_duration:
            break

# Main function to run the program
@click.group()
def main():
    """Main entry point for the script."""
    pass

@main.command()
@click.argument('hotspot_name')
@click.option('--password', default=None, help='Optional custom password for the hotspot.')
def hotspot(hotspot_name, password):
    """Start a hotspot with the specified HOTSPOT_NAME."""
    if not password:
        password = generate_password()  # Generate a random password if not provided
    startHotspot(hotspot_name, password)
    click.echo(f"WiFi Name: {hotspot_name}")
    click.echo(f"Password: {password}")

@main.command()
def capture():
    """Start capturing traffic."""
    captureTraffic()
    click.echo("Traffic capture started.")
    # Display WiFi details and generate QR code


# Run the main function when the script is executed
if __name__ == "__main__":
    main()
