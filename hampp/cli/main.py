"""Command-line interface for HamppServer."""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm, IntPrompt, Prompt
from typing import Optional

from hampp import __version__
from hampp.core.config import Config
from hampp.core.server_manager import ServerManager
from hampp.core.installer import Installer
from hampp.utils.logger import setup_logger, get_log_level_from_verbosity
from hampp.utils.validators import validate_port, validate_directory

console = Console()


def setup_logging(verbosity: int) -> None:
    """Setup logging based on verbosity level."""
    log_level = get_log_level_from_verbosity(verbosity)
    # Configure all loggers to use the specified level
    import logging
    logging.getLogger().setLevel(getattr(logging, log_level))


@click.group()
@click.version_option(version=__version__)
@click.option(
    '-v', '--verbose',
    count=True,
    help='Increase verbosity (use multiple times for more verbose output)'
)
@click.option(
    '--config',
    type=click.Path(),
    help='Path to configuration file'
)
@click.pass_context
def cli(ctx: click.Context, verbose: int, config: Optional[str]) -> None:
    """HamppServer - Modern localhost server manager for Apache, MySQL, and PHP.
    
    A cross-platform server management tool designed for Termux (Android),
    Linux, and other Unix-like systems.
    """
    # Setup logging
    setup_logging(verbose)
    
    # Initialize configuration
    try:
        ctx.ensure_object(dict)
        ctx.obj['config'] = Config(config)
        ctx.obj['server_manager'] = ServerManager(ctx.obj['config'])
        ctx.obj['installer'] = Installer(ctx.obj['config'])
    except Exception as e:
        console.print(f"[red]Error initializing HamppServer: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    '--port', '-p',
    type=int,
    help='Custom port for Apache server'
)
@click.option(
    '--document-root', '-d',
    type=click.Path(),
    help='Custom document root directory'
)
@click.pass_context
def start_apache(ctx: click.Context, port: Optional[int], 
                document_root: Optional[str]) -> None:
    """Start Apache HTTP server."""
    server_manager = ctx.obj['server_manager']
    
    with console.status("[bold green]Starting Apache server..."):
        success = server_manager.start_apache(port, document_root)
    
    if success:
        # Get actual configuration
        config = ctx.obj['config']
        actual_port = port or config.server_config.apache_port
        actual_root = document_root or config.server_config.document_root
        
        console.print(Panel.fit(
            f"[green]✓ Apache server started successfully![/green]\n\n"
            f"[cyan]URL:[/cyan] http://localhost:{actual_port}\n"
            f"[cyan]Document Root:[/cyan] {actual_root}",
            title="Apache Started",
            border_style="green"
        ))
    else:
        console.print("[red]✗ Failed to start Apache server[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def stop_apache(ctx: click.Context) -> None:
    """Stop Apache HTTP server."""
    server_manager = ctx.obj['server_manager']
    
    with console.status("[bold red]Stopping Apache server..."):
        success = server_manager.stop_apache()
    
    if success:
        console.print("[green]✓ Apache server stopped successfully[/green]")
    else:
        console.print("[red]✗ Failed to stop Apache server[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def start_mysql(ctx: click.Context) -> None:
    """Start MySQL/MariaDB server."""
    server_manager = ctx.obj['server_manager']
    
    with console.status("[bold green]Starting MySQL server..."):
        success = server_manager.start_mysql()
    
    if success:
        config = ctx.obj['config']
        
        console.print(Panel.fit(
            f"[green]✓ MySQL server started successfully![/green]\n\n"
            f"[cyan]Port:[/cyan] {config.server_config.mysql_port}\n"
            f"[cyan]Access PHPMyAdmin:[/cyan] http://localhost:{config.server_config.apache_port}/phpmyadmin",
            title="MySQL Started",
            border_style="green"
        ))
    else:
        console.print("[red]✗ Failed to start MySQL server[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def stop_mysql(ctx: click.Context) -> None:
    """Stop MySQL/MariaDB server."""
    server_manager = ctx.obj['server_manager']
    
    with console.status("[bold red]Stopping MySQL server..."):
        success = server_manager.stop_mysql()
    
    if success:
        console.print("[green]✓ MySQL server stopped successfully[/green]")
    else:
        console.print("[red]✗ Failed to stop MySQL server[/red]")
        sys.exit(1)


@cli.command()
@click.argument('service', type=click.Choice(['apache', 'mysql']))
@click.pass_context
def restart(ctx: click.Context, service: str) -> None:
    """Restart a service."""
    server_manager = ctx.obj['server_manager']
    
    with console.status(f"[bold yellow]Restarting {service} server..."):
        success = server_manager.restart_service(service)
    
    if success:
        console.print(f"[green]✓ {service.title()} server restarted successfully[/green]")
    else:
        console.print(f"[red]✗ Failed to restart {service} server[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show status of all services."""
    server_manager = ctx.obj['server_manager']
    config = ctx.obj['config']
    
    # Get status for all services
    all_status = server_manager.get_all_status()
    
    # Create status table
    table = Table(title="HamppServer Status", show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Port", style="blue")
    table.add_column("PID", style="green")
    table.add_column("Uptime", style="yellow")
    table.add_column("Memory", style="red")
    
    for service_name, status in all_status.items():
        # Format status
        if status.running:
            status_text = "[green]Running[/green]"
        else:
            status_text = "[red]Stopped[/red]"
        
        # Format uptime
        if status.uptime:
            hours = int(status.uptime // 3600)
            minutes = int((status.uptime % 3600) // 60)
            uptime_text = f"{hours:02d}:{minutes:02d}"
        else:
            uptime_text = "-"
        
        # Format memory
        if status.memory_usage:
            memory_text = f"{status.memory_usage:.1f}MB"
        else:
            memory_text = "-"
        
        table.add_row(
            status.name,
            status_text,
            str(status.port) if status.port else "-",
            str(status.pid) if status.pid else "-",
            uptime_text,
            memory_text
        )
    
    console.print(table)
    
    # Show quick access URLs if Apache is running
    if all_status['apache'].running:
        apache_port = config.server_config.apache_port
        console.print(f"\n[cyan]Quick Access:[/cyan]")
        console.print(f"  • Main site: http://localhost:{apache_port}")
        console.print(f"  • PHP info: http://localhost:{apache_port}/phpinfo.php")
        
        if config.server_config.enable_phpmyadmin:
            console.print(f"  • PHPMyAdmin: http://localhost:{apache_port}/phpmyadmin")


@cli.command()
@click.option('--force', is_flag=True, help='Force reinstallation')
@click.pass_context
def install(ctx: click.Context, force: bool) -> None:
    """Install HamppServer dependencies."""
    installer = ctx.obj['installer']
    config = ctx.obj['config']
    
    # Show platform information
    platform_info = config.platform.get_info()
    
    console.print(Panel.fit(
        f"[bold]Platform:[/bold] {platform_info['name']}\n"
        f"[bold]Supported:[/bold] {'Yes' if platform_info['supported'] else 'No'}\n"
        f"[bold]Package Manager:[/bold] {platform_info.get('package_manager', 'None')}",
        title="System Information",
        border_style="blue"
    ))
    
    if not platform_info['supported']:
        console.print("[red]This platform is not currently supported[/red]")
        sys.exit(1)
    
    # Confirm installation
    if not force:
        if not Confirm.ask("Do you want to proceed with installation?"):
            console.print("Installation cancelled")
            return
    
    # Run installation
    with console.status("[bold green]Installing dependencies..."):
        success = installer.install_dependencies(force)
    
    if success:
        console.print("[green]✓ Installation completed successfully![/green]")
        console.print("\n[cyan]You can now use 'hampp status' to check server status[/cyan]")
    else:
        console.print("[red]✗ Installation failed[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show current configuration."""
    config = ctx.obj['config']
    config_dict = config.get_config_dict()
    
    # Server configuration
    server_table = Table(title="Server Configuration", show_header=True)
    server_table.add_column("Setting", style="cyan")
    server_table.add_column("Value", style="green")
    
    for key, value in config_dict['server'].items():
        server_table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(server_table)
    
    # Path configuration
    path_table = Table(title="Path Configuration", show_header=True)
    path_table.add_column("Path", style="cyan")
    path_table.add_column("Value", style="green")
    
    for key, value in config_dict['paths'].items():
        if value:  # Only show non-empty paths
            path_table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(path_table)


@cli.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set configuration value."""
    config = ctx.obj['config']
    
    # Validate the configuration
    from hampp.utils.validators import validate_config_value
    
    valid, converted_value, error = validate_config_value(key, value)
    
    if not valid:
        console.print(f"[red]Invalid configuration: {error}[/red]")
        sys.exit(1)
    
    # Update configuration
    try:
        config.update_server_config(**{key: converted_value})
        console.print(f"[green]✓ Configuration updated: {key} = {converted_value}[/green]")
    except Exception as e:
        console.print(f"[red]Error updating configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def config_reset(ctx: click.Context) -> None:
    """Reset configuration to defaults."""
    config = ctx.obj['config']
    
    if Confirm.ask("Are you sure you want to reset all configuration to defaults?"):
        config.reset_to_defaults()
        console.print("[green]✓ Configuration reset to defaults[/green]")
    else:
        console.print("Reset cancelled")


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Start interactive mode."""
    config = ctx.obj['config']
    server_manager = ctx.obj['server_manager']
    
    console.print(Panel.fit(
        "[bold blue]   __ __                       ____                    [/bold blue]\n"
        "[bold blue]  / // /__ ___ _  ___  ___    / __/__ _____  _____ ____[/bold blue]\n"
        "[bold blue] / _  / _ `/  ' \/ _ \/ _ \  _\ \/ -_) __/ |/ / -_) __/[/bold blue]\n"
        "[bold blue]/_//_/\_,_/_/_/_/ .__/ .__/ /___/\__/_/  |___/\__/_/   [/bold blue]\n"
        "[bold blue]               /_/  /_/                                [/bold blue]\n\n"
        "[bold blue]Interactive Mode[/bold blue]\n"
        "[bold green]Author: Md Habibur Rahman[/bold green]\n"
        "[bold green]Facebook: https://facebook.com/yourchocomate[/bold green]\n\n"
        "Welcome to HamppServer! Use the menu below to manage your servers.",
        title=f"HamppServer v{__version__}",
        border_style="blue"
    ))
    
    while True:
        console.print("\n[cyan]Available Actions:[/cyan]")
        console.print("1. Start Apache Server")
        console.print("2. Stop Apache Server")
        console.print("3. Start MySQL Server")
        console.print("4. Stop MySQL Server")
        console.print("5. Show Server Status")
        console.print("6. Configuration")
        console.print("7. Exit")
        
        try:
            choice = IntPrompt.ask("Choose an action", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == 1:
                # Start Apache with custom options
                if Confirm.ask("Use custom port?", default=False):
                    port = IntPrompt.ask("Enter port number", default=config.server_config.apache_port)
                else:
                    port = None
                
                if Confirm.ask("Use custom document root?", default=False):
                    document_root = Prompt.ask("Enter document root path")
                else:
                    document_root = None
                
                ctx.invoke(start_apache, port=port, document_root=document_root)
                
            elif choice == 2:
                ctx.invoke(stop_apache)
                
            elif choice == 3:
                ctx.invoke(start_mysql)
                
            elif choice == 4:
                ctx.invoke(stop_mysql)
                
            elif choice == 5:
                ctx.invoke(status)
                
            elif choice == 6:
                console.print("\n[cyan]Configuration Options:[/cyan]")
                console.print("1. Show Configuration")
                console.print("2. Set Configuration Value")
                console.print("3. Reset to Defaults")
                
                config_choice = IntPrompt.ask("Choose option", choices=["1", "2", "3"])
                
                if config_choice == 1:
                    ctx.invoke(config_show)
                elif config_choice == 2:
                    key = Prompt.ask("Configuration key")
                    value = Prompt.ask("Configuration value")
                    ctx.invoke(config_set, key=key, value=value)
                elif config_choice == 3:
                    ctx.invoke(config_reset)
                    
            elif choice == 7:
                console.print("[cyan]Goodbye![/cyan]")
                break
                
        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


# Add command aliases to the group
cli.add_command(start_apache, name='start')  # Allow 'hampp start' as alias
cli.add_command(config_show, name='config')  # Allow 'hampp config' as alias


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
