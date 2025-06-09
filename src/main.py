"""
Main entry point for the Pepper Robot and Flask Server integration system.
This module provides a unified interface to start either the Flask server
or the Pepper client.
"""

import sys
import argparse
import logging

from src.flask_server.flask_server import run_server
from src.pepper_client.pepper_client import main as run_client
from src.config.config import (
    FLASK_HOST,
    FLASK_PORT,
    DEFAULT_PEPPER_IP,
    PEPPER_PORT
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the system.
    """
    parser = argparse.ArgumentParser(
        description="Pepper Robot and Flask Server Integration System",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Create subparsers for server and client
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Server subparser
    server_parser = subparsers.add_parser("server", help="Run the Flask server")
    server_parser.add_argument("--host", default=FLASK_HOST,
                              help=f"Host to run the server on (default: {FLASK_HOST})")
    server_parser.add_argument("--port", type=int, default=FLASK_PORT,
                              help=f"Port to run the server on (default: {FLASK_PORT})")
    
    # Client subparser
    client_parser = subparsers.add_parser("client", help="Run the Pepper client")
    client_parser.add_argument("pepper_ip", nargs="?", default=DEFAULT_PEPPER_IP,
                              help=f"IP address of the Pepper robot (default: {DEFAULT_PEPPER_IP})")
    client_parser.add_argument("--port", type=int, default=PEPPER_PORT,
                              help=f"Port number for the Pepper robot (default: {PEPPER_PORT})")
    client_parser.add_argument("--server-host", default=FLASK_HOST,
                              help=f"Host of the Flask server (default: {FLASK_HOST})")
    client_parser.add_argument("--server-port", type=int, default=FLASK_PORT,
                              help=f"Port of the Flask server (default: {FLASK_PORT})")
    client_parser.add_argument("--once", action="store_true",
                              help="Run only once instead of continuously")
    client_parser.add_argument("--interval", type=float, default=1.0,
                              help="Time interval between processing cycles in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    if args.command == "server":
        # Override global config with command-line arguments
        import src.config.config as config
        config.FLASK_HOST = args.host
        config.FLASK_PORT = args.port
        
        # Run the server
        logger.info(f"Starting Flask server on {args.host}:{args.port}")
        run_server()
        
    elif args.command == "client":
        # Run the client
        logger.info(f"Starting Pepper client connecting to {args.pepper_ip}:{args.port}")
        # We need to reconstruct sys.argv for the client's argparse
        sys.argv = [
            "pepper_client.py",
            args.pepper_ip,
            "--port", str(args.port),
            "--server-host", args.server_host,
            "--server-port", str(args.server_port),
            "--interval", str(args.interval)
        ]
        if args.once:
            sys.argv.append("--once")
        
        run_client()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()