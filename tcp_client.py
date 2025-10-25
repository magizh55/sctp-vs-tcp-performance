#!/usr/bin/env python3
"""
TCP Client Implementation with Performance Metrics
Sends data to TCP server and measures latency and throughput
"""

import socket
import time
import json
import sys
from datetime import datetime

class TCPClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.socket = None
        self.metrics = {
            'total_messages_sent': 0,
            'total_bytes_sent': 0,
            'latencies': [],  # Round-trip times for each message
            'send_times': [],
            'start_time': None,
            'end_time': None,
            'failed_messages': 0
        }
        
    def connect(self):
        """Establish connection to TCP server"""
        try:
            # Create TCP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Connect to server
            print(f"[TCP CLIENT] Connecting to {self.host}:{self.port}...")
            self.socket.connect((self.host, self.port))
            print(f"[TCP CLIENT] Connected successfully!\n")
            
            return True
            
        except Exception as e:
            print(f"[TCP CLIENT ERROR] Connection failed: {e}")
            return False
            
    def send_message(self, message):
        """Send a single message and measure latency"""
        try:
            # Record send time
            send_start = time.time()
            
            # Send message
            if isinstance(message, str):
                message_bytes = message.encode('utf-8')
            else:
                message_bytes = message
                
            self.socket.send(message_bytes)
            
            # Wait for acknowledgment
            ack = self.socket.recv(1024)
            
            # Record receive time and calculate latency
            send_end = time.time()
            latency = send_end - send_start
            
            # Update metrics
            self.metrics['total_messages_sent'] += 1
            self.metrics['total_bytes_sent'] += len(message_bytes)
            self.metrics['latencies'].append(latency)
            self.metrics['send_times'].append(send_start)
            
            return True, latency
            
        except Exception as e:
            print(f"[TCP CLIENT ERROR] Send failed: {e}")
            self.metrics['failed_messages'] += 1
            return False, 0
            
    def send_bulk_messages(self, num_messages=100, message_size=1024):
        """Send multiple messages for performance testing"""
        print(f"[TCP CLIENT] Starting bulk send test...")
        print(f"[TCP CLIENT] Messages: {num_messages}, Size: {message_size} bytes\n")
        
        self.metrics['start_time'] = time.time()
        
        # Generate test message
        test_message = "X" * message_size
        
        # Send messages
        for i in range(num_messages):
            success, latency = self.send_message(test_message)
            
            if success:
                if (i + 1) % 10 == 0:  # Print progress every 10 messages
                    print(f"[TCP CLIENT] Sent {i + 1}/{num_messages} messages, "
                          f"Last latency: {latency*1000:.2f} ms")
            else:
                print(f"[TCP CLIENT] Failed to send message {i + 1}")
                
        self.metrics['end_time'] = time.time()
        
        print(f"\n[TCP CLIENT] Bulk send complete!\n")
        
    def send_variable_load(self, duration_seconds=10, messages_per_second=10, message_size=1024):
        """Send messages at a controlled rate for specified duration"""
        print(f"[TCP CLIENT] Starting variable load test...")
        print(f"[TCP CLIENT] Duration: {duration_seconds}s, "
              f"Rate: {messages_per_second} msg/s, Size: {message_size} bytes\n")
        
        self.metrics['start_time'] = time.time()
        
        # Generate test message
        test_message = "Y" * message_size
        
        # Calculate inter-message delay
        delay = 1.0 / messages_per_second
        
        end_time = time.time() + duration_seconds
        message_count = 0
        
        while time.time() < end_time:
            send_start = time.time()
            
            success, latency = self.send_message(test_message)
            message_count += 1
            
            if success and message_count % messages_per_second == 0:
                elapsed = time.time() - self.metrics['start_time']
                print(f"[TCP CLIENT] {message_count} messages sent in {elapsed:.1f}s, "
                      f"Last latency: {latency*1000:.2f} ms")
            
            # Sleep to maintain desired rate
            elapsed = time.time() - send_start
            if elapsed < delay:
                time.sleep(delay - elapsed)
                
        self.metrics['end_time'] = time.time()
        
        print(f"\n[TCP CLIENT] Variable load test complete!\n")
        
    def disconnect(self):
        """Close connection to server"""
        if self.socket:
            self.socket.close()
            print("[TCP CLIENT] Disconnected from server\n")
            
    def display_metrics(self):
        """Display client performance metrics"""
        print("="*60)
        print("TCP CLIENT PERFORMANCE METRICS")
        print("="*60)
        
        if self.metrics['start_time'] and self.metrics['end_time']:
            duration = self.metrics['end_time'] - self.metrics['start_time']
            print(f"Duration: {duration:.2f} seconds")
            
        print(f"Total Messages Sent: {self.metrics['total_messages_sent']}")
        print(f"Total Bytes Sent: {self.metrics['total_bytes_sent']:,} bytes")
        print(f"Failed Messages: {self.metrics['failed_messages']}")
        
        if len(self.metrics['latencies']) > 0:
            latencies_ms = [l * 1000 for l in self.metrics['latencies']]
            avg_latency = sum(latencies_ms) / len(latencies_ms)
            min_latency = min(latencies_ms)
            max_latency = max(latencies_ms)
            
            print(f"\nLatency Statistics:")
            print(f"  Average: {avg_latency:.2f} ms")
            print(f"  Min: {min_latency:.2f} ms")
            print(f"  Max: {max_latency:.2f} ms")
            
            # Calculate percentiles
            sorted_latencies = sorted(latencies_ms)
            p50 = sorted_latencies[len(sorted_latencies) // 2]
            p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)]
            
            print(f"  P50: {p50:.2f} ms")
            print(f"  P95: {p95:.2f} ms")
            print(f"  P99: {p99:.2f} ms")
            
        if self.metrics['total_messages_sent'] > 0 and self.metrics['start_time']:
            duration = self.metrics['end_time'] - self.metrics['start_time']
            if duration > 0:
                msg_per_sec = self.metrics['total_messages_sent'] / duration
                throughput = (self.metrics['total_bytes_sent'] * 8) / duration / 1_000_000  # Mbps
                
                print(f"\nThroughput:")
                print(f"  Messages per Second: {msg_per_sec:.2f}")
                print(f"  Throughput: {throughput:.2f} Mbps")
                print(f"  Average Message Size: {self.metrics['total_bytes_sent'] / self.metrics['total_messages_sent']:.2f} bytes")
        
        print("="*60 + "\n")
        
        # Save metrics to file
        self.save_metrics()
        
    def save_metrics(self):
        """Save metrics to JSON file for analysis"""
        metrics_file = f"tcp_client_metrics_{int(time.time())}.json"
        
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
        print(f"[TCP CLIENT] Metrics saved to {metrics_file}")
        
    def get_metrics(self):
        """Return metrics dictionary"""
        return self.metrics

def main():
    """Main function to run TCP client tests"""
    client = TCPClient(host='127.0.0.1', port=5000)
    
    # Connect to server
    if not client.connect():
        print("[TCP CLIENT] Failed to connect. Make sure server is running.")
        sys.exit(1)
        
    try:
        # Test 1: Bulk send test
        client.send_bulk_messages(num_messages=100, message_size=1024)
        
        # Small delay between tests
        time.sleep(1)
        
        # Test 2: Variable load test
        client.send_variable_load(duration_seconds=10, messages_per_second=10, message_size=512)
        
    except KeyboardInterrupt:
        print("\n[TCP CLIENT] Test interrupted by user")
    finally:
        # Disconnect and display metrics
        client.disconnect()
        client.display_metrics()

if __name__ == "__main__":
    main()
