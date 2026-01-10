"""
Main TUI application using Textual.

A beautiful terminal interface for downloading ISO images.
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, ProgressBar, Button, Label
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual import events, on, work
from rich.text import Text
from datetime import datetime
import asyncio

from iso_toolkit.models import OSCategory, OSInfo, DownloadState, DownloadProgress
from iso_toolkit.manager import DownloadManager
from iso_toolkit.os.base import get_registry, register_provider
from iso_toolkit.os.windows import WindowsProvider
from iso_toolkit.os.linux import LinuxProvider


class ISOToolkitApp(App):
    """
    Main application class for ISO Toolkit TUI.
    """

    TITLE = "ISO Toolkit"
    SUB_TITLE = "Multi-OS ISO Downloader"
    CSS_PATH = "styles.css"

    def __init__(self):
        super().__init__()
        self.download_manager = DownloadManager()
        self._setup_providers()

    def _setup_providers(self):
        """Register OS providers."""
        registry = get_registry()
        registry.register(WindowsProvider())
        registry.register(LinuxProvider())

    def on_mount(self) -> None:
        """Initialize app on mount."""
        self.push_screen(MainScreen())

    def compose(self) -> ComposeResult:
        """Compose the main screen."""
        yield Header()
        yield Footer()


class MainScreen(Screen):
    """Main menu screen for OS category selection."""

    def compose(self) -> ComposeResult:
        """Compose the main menu."""
        yield Container(
            Static(
                "[bold cyan]🖥️  ISO Toolkit[/bold cyan]\n"
                "[dim]Multi-OS ISO Downloader Toolkit[/dim]\n\n"
                "Select an OS category to browse available ISOs:",
                id="welcome-text"
            ),
            Container(
                Button("🪟  Windows", id="btn-windows", variant="primary"),
                Button("🐧  Linux", id="btn-linux", variant="primary"),
                Button("🍎  macOS (N/A)", id="btn-macos", variant="default", disabled=True),
                Button("📁  Downloads", id="btn-downloads", variant="success"),
                Button("⚙️  Settings", id="btn-settings", variant="default"),
                Button("❌  Quit", id="btn-quit", variant="error"),
                id="menu-buttons"
            ),
            id="main-container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-windows":
            self.app.push_screen(OSListScreen(OSCategory.WINDOWS))
        elif button_id == "btn-linux":
            self.app.push_screen(OSListScreen(OSCategory.LINUX))
        elif button_id == "btn-downloads":
            self.app.push_screen(DownloadsScreen())
        elif button_id == "btn-settings":
            self.app.push_screen(SettingsScreen())
        elif button_id == "btn-quit":
            self.app.exit()


class OSListScreen(Screen):
    """Screen for listing available OS ISOs."""

    def __init__(self, category: OSCategory):
        super().__init__()
        self.category = category
        self.os_list: list[OSInfo] = []

    def compose(self) -> ComposeResult:
        """Compose the OS list screen."""
        category_name = self.category.value.title()

        yield Container(
            Static(f"[bold]{self._get_category_icon()} {category_name} ISOs[/bold]", id="screen-title"),
            DataTable(id="os-table"),
            Container(
                Button("⟵  Back", id="btn-back", variant="default"),
                Button("⬇️  Download", id="btn-download", variant="primary", disabled=True),
                Button("🔄  Refresh", id="btn-refresh", variant="default"),
                id="list-buttons"
            ),
            id="os-list-container"
        )

    def _get_category_icon(self) -> str:
        """Get icon for current category."""
        icons = {
            OSCategory.WINDOWS: "🪟",
            OSCategory.LINUX: "🐧",
            OSCategory.MACOS: "🍎",
            OSCategory.BSD: "🦞",
        }
        return icons.get(self.category, "💿")

    def on_mount(self) -> None:
        """Load OS list on mount."""
        self._load_os_list()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        self.query_one("#btn-download", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-download":
            self._start_download()
        elif button_id == "btn-refresh":
            self._load_os_list()

    def _load_os_list(self):
        """Load the list of available OS ISOs."""
        @work(exclusive=True)
        async def load_list(screen: OSListScreen):
            table = screen.query_one(DataTable)
            table.clear(columns=True)

            # Add columns
            table.add_column("OS", width=25)
            table.add_column("Version", width=15)
            table.add_column("Arch", width=8)
            table.add_column("Size", width=12)
            table.add_column("Source", width=15)

            table.loading = True

            # Fetch OS list
            registry = get_registry()
            providers = registry.get_by_category(screen.category)
            screen.os_list = []

            for provider in providers:
                try:
                    os_list = await provider.fetch_available()
                    screen.os_list.extend(os_list)
                except Exception as e:
                    pass

            # Populate table
            for os_info in screen.os_list:
                table.add_row(
                    f"{os_info.icon or ''} {os_info.name}",
                    os_info.version,
                    os_info.architecture.value,
                    os_info.size_formatted,
                    os_info.source or "Unknown"
                )

            table.loading = False

        load_list(self)

    def _start_download(self):
        """Start the selected download."""
        table = self.query_one(DataTable)
        if table.cursor_row is None:
            return

        os_info = self.os_list[table.cursor_row]
        self.app.push_screen(DownloadScreen(os_info))


class DownloadScreen(Screen):
    """Screen for active download with progress display."""

    def __init__(self, os_info: OSInfo):
        super().__init__()
        self.os_info = os_info
        self.download_manager = self.app.download_manager
        self.task = None
        self._finished = False

    def compose(self) -> ComposeResult:
        """Compose the download screen."""
        yield Container(
            Static(f"[bold]⬇️  Downloading: {self.os_info.display_name}[/bold]", id="download-title"),
            Static(f"📁 {self.os_info.name} {self.os_info.version} - {self.os_info.architecture.value}", id="download-info"),
            Static(f"🌐 {self.os_info.url[:60]}..." if len(self.os_info.url) > 60 else f"🌐 {self.os_info.url}", id="download-url"),
            Container(
                Label("Progress:", id="progress-label"),
                ProgressBar(id="progress-bar", show_eta=True),
                Static(
                    "• Downloaded: [bold]0 B / 0 B[/bold]\n"
                    "• Speed: [bold]0 B/s[/bold]\n"
                    "• ETA: [bold]--[/bold]\n"
                    "• Status: [bold yellow]Starting...[/bold yellow]",
                    id="download-stats"
                ),
                id="progress-container"
            ),
            Container(
                Button("⟵  Back", id="btn-back", variant="default"),
                Button("⏸️  Pause", id="btn-pause", variant="default"),
                Button("❌  Cancel", id="btn-cancel", variant="error"),
                id="download-buttons"
            ),
            id="download-container"
        )

    def on_mount(self) -> None:
        """Start download on mount."""
        self._start_download()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            if not self._finished and self.task and self.task.state == DownloadState.DOWNLOADING:
                self.app.pop_screen()
            else:
                self.app.pop_screen()

        elif button_id == "btn-cancel":
            if self.task:
                self.download_manager.cancel_download(self.task)
                self._finished = True
                self.query_one("#download-stats", Static).update(
                    "• Downloaded: [bold]Cancelled[/bold]\n"
                    "• Status: [bold red]Download Cancelled[/bold red]"
                )
                self.query_one("#btn-cancel", Button).disabled = True
                self.query_one("#btn-pause", Button).disabled = True

    def _start_download(self):
        """Start the download process."""
        # Create download task
        self.task = self.download_manager.create_download_task(self.os_info)

        # Set up progress callback
        def on_progress(progress: DownloadProgress):
            self._update_progress(progress)

        self.task.on_progress = on_progress
        self.task.on_complete = self._on_download_complete

        # Start download
        self.download_manager.start_download(self.task)

    def _update_progress(self, progress: DownloadProgress):
        """Update the progress display."""
        self.app.call_from_thread(self._do_update_progress, progress)

    def _do_update_progress(self, progress: DownloadProgress):
        """Update progress from main thread."""
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        stats = self.query_one("#download-stats", Static)

        # Update progress bar
        if progress.total > 0:
            progress_bar.progress = progress.percentage
            progress_bar.total = 100

        # Update stats
        state_text = "Downloading..."
        if self.task:
            if self.task.state == DownloadState.VERIFYING:
                state_text = "[bold cyan]Verifying checksum...[/bold cyan]"
            elif self.task.state == DownloadState.COMPLETED:
                state_text = "[bold green]✓ Download Complete[/bold green]"

        stats.update(
            f"• Downloaded: [bold]{progress.downloaded_formatted} / {progress.total_formatted}[/bold]\n"
            f"• Speed: [bold]{progress.speed_formatted}[/bold]\n"
            f"• ETA: [bold]{progress.eta_formatted}[/bold]\n"
            f"• Status: {state_text}\n"
            f"• {progress.percentage:.1f}% Complete"
        )

        if self.task and self.task.state == DownloadState.COMPLETED:
            self._on_finished()

    def _on_download_complete(self, success: bool, error: str = None):
        """Handle download completion."""
        self.app.call_from_thread(self._do_on_complete, success, error)

    def _do_on_complete(self, success: bool, error: str = None):
        """Handle completion from main thread."""
        stats = self.query_one("#download-stats", Static)

        if success:
            stats.update(
                f"• Downloaded: [bold green]✓ {self.os_info.size_formatted}[/bold green]\n"
                f"• Status: [bold green]✓ Download Complete & Verified[/bold green]\n"
                f"• Saved to: {self.task.output_path}"
            )
        else:
            stats.update(
                f"• Status: [bold red]✗ Download Failed[/bold red]\n"
                f"• Error: {error or 'Unknown error'}"
            )

        self._finished = True
        self._on_finished()

    def _on_finished(self):
        """Handle download finished state."""
        self.query_one("#btn-pause", Button).disabled = True
        self.query_one("#btn-cancel", Button).disabled = True


class DownloadsScreen(Screen):
    """Screen showing download history and active downloads."""

    def compose(self) -> ComposeResult:
        """Compose the downloads screen."""
        yield Container(
            Static("[bold]📁 Download Manager[/bold]", id="downloads-title"),
            DataTable(id="downloads-table"),
            Container(
                Button("⟵  Back", id="btn-back", variant="default"),
                Button("🗑️  Clear Completed", id="btn-clear", variant="default"),
                id="downloads-buttons"
            ),
            id="downloads-container"
        )

    def on_mount(self) -> None:
        """Load downloads list on mount."""
        self._load_downloads()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-clear":
            self.app.download_manager.clear_completed()
            self._load_downloads()

    def _load_downloads(self):
        """Load and display download history."""
        table = self.query_one(DataTable)
        table.clear(columns=True)

        table.add_column("OS", width=25)
        table.add_column("Status", width=12)
        table.add_column("Progress", width=12)
        table.add_column("Size", width=12)

        # Get all downloads
        all_downloads = (
            self.app.download_manager.active_tasks +
            self.app.download_manager.completed_tasks
        )

        for task in all_downloads:
            status = task.state.value.title()
            progress = "0%"

            if task.progress:
                progress = f"{task.progress.percentage:.1f}%"

            table.add_row(
                f"{task.os_info.icon or ''} {task.os_info.display_name}",
                status,
                progress,
                task.os_info.size_formatted
            )


class SettingsScreen(Screen):
    """Screen for application settings."""

    def compose(self) -> ComposeResult:
        """Compose the settings screen."""
        download_dir = self.app.download_manager.download_dir

        yield Container(
            Static("[bold]⚙️  Settings[/bold]", id="settings-title"),
            Container(
                Static(f"📁 Download Directory:", id="settings-dir-label"),
                Static(f"[dim]{download_dir}[/dim]", id="settings-dir-value"),
                id="settings-dir-container"
            ),
            Container(
                Static("[dim]More settings coming soon...[/dim]"),
                id="settings-future"
            ),
            Container(
                Button("⟵  Back", id="btn-back", variant="default"),
                id="settings-buttons"
            ),
            id="settings-container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-back":
            self.app.pop_screen()
