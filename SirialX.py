
import sys
import re
import serial
import serial.tools.list_ports
from datetime import datetime
import time

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Button, Header, Footer, Static, Select, RichLog
from textual.worker import Worker, get_current_worker

# --- Notification System Setup ---
try:
    # Use plyer for system notifications, especially on Windows
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    # If plyer is not installed, we disable the feature gracefully
    PLYER_AVAILABLE = False
    notification = None

# --- Configuration ---
BAUD_RATES = [
    ("9600", 9600), ("19200", 19200), ("38400", 38400), ("57600", 57600),
    ("115200", 115200), ("230400", 230400), ("460800", 460800), ("921600", 921600),
]
BOARDS = [
    ("Generic Microcontroller", "generic"), ("ESP32 DevKit v1", "esp32"), ("Arduino Uno", "uno"),
]

# --- The Main Application Class ---

class SerialMonitorApp(App):
    """A Textual app to monitor serial port output."""

    TITLE = "SiriaX Serial Monitor"
    SUB_TITLE = "A TUI for your Microcontroller"
    CSS_PATH = None

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_connection: serial.Serial | None = None
        self.is_connecting = False
        self.read_worker: Worker | None = None
        # Simple regex to find IPv4 addresses
        self.ip_regex = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="app-grid"):
            with VerticalScroll(id="controls-pane"):
                yield Static("Connection Settings", classes="header")
                yield Select([], prompt="Select Port", id="port-select")
                yield Select(BAUD_RATES, prompt="Select Baud Rate", value=115200, id="baud-select")
                yield Select(BOARDS, prompt="Select Board", id="board-select")
                yield Button("Connect", variant="success", id="connect-button")
                yield Button("Restart Device", variant="primary", id="restart-button", disabled=True)
            
            with VerticalScroll(id="log-pane"):
                yield Static("Serial Output", classes="header")
                yield RichLog(highlight=True, markup=True, id="serial-log")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        self.update_port_list()
        log = self.query_one(RichLog)
        log.write("[bold green]Welcome to the Serial Monitor![/bold green]")
        log.write("Select your port and baud rate, then press 'Connect'.")
        if not PLYER_AVAILABLE and sys.platform == "win32":
            self.notify(
                "Install 'plyer' for desktop notifications.",
                title="Optional Feature",
                severity="warning",
                timeout=10,
            )

    def update_port_list(self):
        """Scan for serial ports and update the Select widget."""
        port_select = self.query_one("#port-select")
        try:
            ports = serial.tools.list_ports.comports()
            port_list = [(f"{p.device}: {p.description}", p.device) for p in ports]
            
            if not port_list:
                port_select.set_options([("No ports found", None)])
                self.notify("No serial ports found.", title="Scan Complete", severity="warning")
            else:
                port_select.set_options(port_list)
                # Auto-select a common port
                for _, device in port_list:
                    if "USB" in device.upper() or "ACM" in device.upper() or "COM" in device.upper():
                        port_select.value = device
                        break
                else: # if no preferred port is found, select the first one
                    port_select.value = port_list[0][1]
        except Exception as e:
            self.notify(f"Could not scan for ports: {e}", title="Error", severity="error")
            port_select.set_options([("Error scanning ports", None)])

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the button presses."""
        if event.button.id == "connect-button":
            if self.serial_connection and self.serial_connection.is_open:
                await self.disconnect()
            else:
                await self.connect()
        elif event.button.id == "restart-button":
            await self.restart_device()
    
    async def connect(self):
        """Establish a serial connection."""
        if self.is_connecting: return

        self.is_connecting = True
        port = self.query_one("#port-select").value
        baud = self.query_one("#baud-select").value
        log = self.query_one(RichLog)

        if not port or not baud:
            self.notify("Port and Baud Rate must be selected.", title="Connection Error", severity="error")
            self.is_connecting = False
            return

        try:
            log.write(f"Attempting to connect to {port} at {baud} bps...")
            self.serial_connection = serial.Serial(port, int(baud), timeout=0.1)
            
            self.query_one("#connect-button").label = "Disconnect"
            self.query_one("#connect-button").variant = "error"
            self.query_one("#port-select").disabled = True
            self.query_one("#baud-select").disabled = True
            self.query_one("#restart-button").disabled = False
            
            log.write(f"[bold green]Successfully connected to {self.serial_connection.name}[/bold green]")
            self.notify(f"Connected to {port}", title="Success")
            self.read_worker = self.run_worker(self.read_from_serial, thread=True)

        except (serial.SerialException, ValueError, OSError) as e:
            log.write(f"[bold red]Connection failed: {e}[/bold red]")
            self.notify(f"Connection failed: {e}", title="Error", severity="error", timeout=10)
            self.serial_connection = None
        except Exception as e:
            log.write(f"[bold red]An unexpected error occurred: {e}[/bold red]")
            self.notify(f"An unexpected error occurred: {e}", title="Critical Error", severity="error", timeout=10)
            self.serial_connection = None
        finally:
            self.is_connecting = False

    async def disconnect(self):
        """Close the serial connection safely."""
        worker_to_cancel = self.read_worker
        if worker_to_cancel:
            self.read_worker = None
            await worker_to_cancel.cancel()
        
        if self.serial_connection:
            try:
                self.serial_connection.close()
            except serial.SerialException as e:
                self.query_one(RichLog).write(f"[bold red]Error closing port: {e}[/bold red]")
                self.notify(f"Error closing port: {e}", title="Disconnect Error", severity="error")
            self.serial_connection = None
            
        self.query_one("#connect-button").label = "Connect"
        self.query_one("#connect-button").variant = "success"
        self.query_one("#port-select").disabled = False
        self.query_one("#baud-select").disabled = False
        self.query_one("#restart-button").disabled = True
        self.query_one(RichLog).write("[bold yellow]Disconnected.[/bold yellow]")
        self.notify("Disconnected from serial port.", title="Status")

    async def restart_device(self):
        """Signal the device to restart by toggling DTR/RTS lines."""
        if self.serial_connection and self.serial_connection.is_open:
            log = self.query_one(RichLog)
            log.write("[bold yellow]Sending restart signal to device...[/bold yellow]")
            self.notify("Sending restart signal...", title="Device Control")
            self.run_worker(self.perform_restart_sequence, thread=True)
        else:
            self.notify("Cannot restart: Not connected.", title="Error", severity="error")

    def perform_restart_sequence(self) -> None:
        """The actual DTR/RTS toggle logic that runs in a thread."""
        if not self.serial_connection: return
        try:
            self.serial_connection.dtr = False
            self.serial_connection.rts = False
            time.sleep(0.1)
            self.serial_connection.dtr = True
            self.serial_connection.rts = True
            self.call_from_thread(self.post_message_to_log, "[bold green]Restart signal sent. Device should be rebooting.[/bold green]")
            self.call_from_thread(self.notify, "Restart signal sent successfully.", title="Device Control")
        except (serial.SerialException, AttributeError) as e:
            self.call_from_thread(self.post_message_to_log, f"[bold red]Failed to send restart signal: {e}[/bold red]")
            self.call_from_thread(self.notify, f"Failed to send restart signal: {e}", title="Error", severity="error")

    def read_from_serial(self) -> None:
        """Worker thread to read serial data continuously."""
        worker = get_current_worker()
        while not worker.is_cancelled:
            try:
                if self.serial_connection and self.serial_connection.is_open:
                    line = self.serial_connection.readline()
                    if line:
                        message = line.decode('utf-8', errors='replace').strip()
                        self.call_from_thread(self.post_message_to_log, message)

                        # Check for IP address and send system notification
                        ip_match = self.ip_regex.search(message)
                        if ip_match:
                            ip_address = ip_match.group(0)
                            self.send_system_notification(
                                title="IP Address Detected",
                                message=f"Device reported IP: {ip_address}"
                            )

            except serial.SerialException:
                self.call_from_thread(self.post_message_to_log, "[bold red]Error: Device disconnected or port error.[/bold red]")
                self.call_from_thread(self.notify, "Device disconnected or port error.", title="Connection Lost", severity="error")
                self.call_from_thread(self.disconnect)
                break
            except Exception as e:
                self.call_from_thread(self.post_message_to_log, f"[bold red]An unexpected error occurred in reader thread: {e}[/bold red]")
                self.call_from_thread(self.notify, "An error occurred while reading.", title="Worker Error", severity="error")
                break # Exit the worker loop on any other error
    
    def post_message_to_log(self, message: str) -> None:
        """A thread-safe method to write to the RichLog."""
        if message:
            log = self.query_one(RichLog)
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            log.write(f"[dim]{timestamp}[/dim] {message}")

    def send_system_notification(self, title: str, message: str) -> None:
        """Sends a desktop notification, primarily for Windows."""
        if PLYER_AVAILABLE and sys.platform == "win32":
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Python Serial Monitor",
                    timeout=10,  # Notification will disappear after 10 seconds
                )
            except Exception as e:
                # This can happen if the notification service fails
                self.call_from_thread(self.post_message_to_log, f"[yellow]System notification failed: {e}[/yellow]")

    async def on_unmount(self) -> None:
        """Ensure disconnection when the app is closed."""
        if self.serial_connection and self.serial_connection.is_open:
            await self.disconnect()

# --- Main execution ---
if __name__ == "__main__":
    app = SerialMonitorApp()
    app.run()