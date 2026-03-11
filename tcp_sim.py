#!/usr/bin/env python3
"""tcp_sim — TCP state machine + sliding window simulation. Zero deps."""

TCP_STATES = {
    ('CLOSED', 'active_open'): 'SYN_SENT',
    ('CLOSED', 'passive_open'): 'LISTEN',
    ('LISTEN', 'syn_recv'): 'SYN_RCVD',
    ('SYN_SENT', 'syn_ack_recv'): 'ESTABLISHED',
    ('SYN_RCVD', 'ack_recv'): 'ESTABLISHED',
    ('ESTABLISHED', 'close'): 'FIN_WAIT_1',
    ('ESTABLISHED', 'fin_recv'): 'CLOSE_WAIT',
    ('FIN_WAIT_1', 'ack_recv'): 'FIN_WAIT_2',
    ('FIN_WAIT_1', 'fin_recv'): 'CLOSING',
    ('FIN_WAIT_2', 'fin_recv'): 'TIME_WAIT',
    ('CLOSING', 'ack_recv'): 'TIME_WAIT',
    ('TIME_WAIT', 'timeout'): 'CLOSED',
    ('CLOSE_WAIT', 'close'): 'LAST_ACK',
    ('LAST_ACK', 'ack_recv'): 'CLOSED',
}

class TCPStateMachine:
    def __init__(self):
        self.state = 'CLOSED'
        self.history = ['CLOSED']

    def transition(self, event):
        key = (self.state, event)
        if key in TCP_STATES:
            self.state = TCP_STATES[key]
            self.history.append(self.state)
            return True
        return False

class SlidingWindow:
    def __init__(self, window_size=4):
        self.window_size = window_size
        self.base = 0
        self.next_seq = 0
        self.buffer = {}
        self.acked = set()

    def send(self, data):
        if self.next_seq - self.base >= self.window_size:
            return None
        seq = self.next_seq
        self.buffer[seq] = data
        self.next_seq += 1
        return seq

    def ack(self, seq):
        self.acked.add(seq)
        while self.base in self.acked:
            self.acked.discard(self.base)
            del self.buffer[self.base]
            self.base += 1

    @property
    def in_flight(self):
        return self.next_seq - self.base

def main():
    # TCP state machine demo
    tcp = TCPStateMachine()
    events = ['active_open', 'syn_ack_recv', 'close', 'ack_recv', 'fin_recv', 'timeout']
    print("TCP State Machine:")
    for event in events:
        old = tcp.state
        tcp.transition(event)
        print(f"  {old} --{event}--> {tcp.state}")

    # Sliding window demo
    print(f"\nSliding Window (size=4):")
    sw = SlidingWindow(4)
    for i in range(6):
        seq = sw.send(f"pkt{i}")
        if seq is not None:
            print(f"  Send seq={seq}, in_flight={sw.in_flight}")
        else:
            print(f"  Window full! in_flight={sw.in_flight}")
            sw.ack(sw.base)
            print(f"  ACK {sw.base-1}, in_flight={sw.in_flight}")
            seq = sw.send(f"pkt{i}")
            print(f"  Send seq={seq}, in_flight={sw.in_flight}")

if __name__ == "__main__":
    main()
