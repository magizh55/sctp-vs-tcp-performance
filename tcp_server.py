#!/usr/bin/env python3
"""
TCP Server Implementation with Performance Metrics
Measures latency, throughput, and connection handling performance
"""

import socket
import time
import json
import threading
from datetime import datetime

class TCPServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.metrics = {
            'total_connections': 0,
            'total_bytes_received': 0,
            'total_messages': 0,
            'start_time': None,
            'end_time': None,
            'message_timestamps': []
        }
        
    def start(self):
        """Start the TCP server"""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to address and port
            self.server_socket.bind((self.host, self.port))
            
            # Listen for connections (max 5 queued connections)
            self.server_socket.listen(5)
            
            print(f"[TCP SERVER] Started on {self.host}:{self.port}")
            print(f"[TCP SERVER] Waiting for connections...")
            
            self.metrics['start_time'] = time.time()
            
            # Accept connections
            while True:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.metrics['total_connections'] += 1
                    print(f"\n[TCP SERVER] Connection #{self.metrics['total_connections']} from {client_address}")
                    
                    # Handle client in a new thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.start()
                    
                except KeyboardInterrupt:
                    print("\n[TCP SERVER] Shutting down...")
                    break
                    
        except Exception as e:
            print(f"[TCP SERVER ERROR] {e}")
        finally:
            self.cleanup()
            
    def handle_client(self, client_socket, client_address):
        """Handle individual client connection"""
        try:
            while True:
                # Receive data from client
                data = client_socket.recv(4096)
                
                if not data:
                    break
                    
                # Record timestamp for latency calculation
                receive_time = time.time()
                self.metrics['message_timestamps'].append(receive_time)
                
                # Update metrics
                self.metrics['total_bytes_received'] += len(data)
                self.metrics['total_messages'] += 1
                
                # Decode and print received message
                try:
                    message = data.decode('utf-8')
                    print(f"[TCP SERVER] Received: {message[:50]}... ({len(data)} bytes)")
                except:
                    print(f"[TCP SERVER] Received binary data ({len(data)} bytes)")
                
                # Send acknowledgment back to client
                ack = f"ACK:{self.metrics['total_messages']}"
                client_socket.send(ack.encode('utf-8'))
                
        except Exception as e:
            print(f"[TCP SERVER ERROR] Client handler: {e}")
        finally:
            client_socket.close()
            print(f"[TCP SERVER] Connection from {client_address} closed")
            
    def cleanup(self):
        """Clean up resources and display metrics"""
        self.metrics['end_time'] = time.time()
        
        if self.server_socket:
            self.server_socket.close()
            
        # Calculate and display metrics
        self.display_metrics()
        
    def display_metrics(self):
        """Display server performance metrics"""
        print("\n" + "="*60)
        print("TCP SERVER PERFORMANCE METRICS")
        print("="*60)
        
        if self.metrics['start_time'] and self.metrics['end_time']:
            duration = self.metrics['end_time'] - self.metrics['start_time']
            print(f"Duration: {duration:.2f} seconds")
            
        print(f"Total Connections: {self.metrics['total_connections']}")
        print(f"Total Messages Received: {self.metrics['total_messages']}")
        print(f"Total Bytes Received: {self.metrics['total_bytes_received']:,} bytes")
        
        if self.metrics['total_messages'] > 0 and self.metrics['start_time']:
            duration = self.metrics['end_time'] - self.metrics['start_time']
            if duration > 0:
                msg_per_sec = self.metrics['total_messages'] / duration
                throughput = (self.metrics['total_bytes_received'] * 8) / duration / 1_000_000  # Mbps
                print(f"Messages per Second: {msg_per_sec:.2f}")
                print(f"Throughput: {throughput:.2f} Mbps")
                print(f"Average Message Size: {self.metrics['total_bytes_received'] / self.metrics['total_messages']:.2f} bytes")
        
        print("="*60 + "\n")
        
        # Save metrics to file
        self.save_metrics()
        
    def save_metrics(self):
        """Save metrics to JSON file for analysis"""
        metrics_file = f"tcp_server_metrics_{int(time.time())}.json"
        
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
        print(f"[TCP SERVER] Metrics saved to {metrics_file}")

if __name__ == "__main__":
    # Create and start TCP server
    server = TCPServer(host='127.0.0.1', port=5000)
    server.start()
