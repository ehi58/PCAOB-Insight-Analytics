import subprocess
import time

def run_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()

def vpn_cycle():
    end_time = time.time() + 4 * 60 * 60  # Run for 3 hours
    while time.time() < end_time:
        # Connect to VPN
        run_command("expressvpn connect")
        print("Connected to VPN")
        time.sleep(11 * 60)  # Wait for 11 minutes
        
        # Disconnect from VPN
        run_command("expressvpn disconnect")
        print("Disconnected from VPN")
        time.sleep(7)  # Wait for 7 seconds
        
        # Connect to VPN again
        run_command("expressvpn connect")
        print("Reconnected to VPN")

if __name__ == "__main__":
    vpn_cycle()