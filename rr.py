import sys
from collections import deque

class Process:
    def __init__(self, name: str, arrival: int, burst: int):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_time = burst
        self.start_time = -1
        self.finish_time = -1
    
    def __repr__(self):
        return f"Process(name='{self.name}', arrival={self.arrival}, burst={self.burst})"
    
    def __str__(self):
        return f"Process {self.name}: Arrival Time = {self.arrival}, Burst Time = {self.burst}"

def round_robin_scheduling(processes, time_slice, run_for):
    queue = deque()
    processes.sort(key=lambda x: x.arrival)
    time = 0  # Start time at 0
    scheduled = []
    process_map = {p.name: p for p in processes}

    while time < run_for:
        # Add all processes that have arrived by the current time to the queue
        while processes and processes[0].arrival <= time:
            arriving_process = processes.pop(0)
            scheduled.append((time, arriving_process.name, "arrived"))
            queue.append(arriving_process)

        if queue:
            current_process = queue.popleft()
            if current_process.start_time == -1:
                current_process.start_time = time

            run_time = min(current_process.remaining_time, time_slice)
            scheduled.append((time, current_process.name, "selected", current_process.remaining_time))

            # Execute the current process for the time slice or until it finishes
            for _ in range(run_time):
                time += 1
                current_process.remaining_time -= 1

                # Check for newly arriving processes during execution
                while processes and processes[0].arrival <= time:
                    arriving_process = processes.pop(0)
                    scheduled.append((time, arriving_process.name, "arrived"))
                    queue.append(arriving_process)

                # If the current time exceeds the run_for limit, stop execution
                if time >= run_for:
                    break

            if current_process.remaining_time == 0:
                current_process.finish_time = time
                scheduled.append((time, current_process.name, "finished"))
            else:
                queue.append(current_process)
        else:
            if processes:
                time = processes[0].arrival
            else:
                time += 1
                scheduled.append((time, "Idle"))

    return scheduled, time, process_map

def print_scheduling(scheduled, total_time, processes, process_map=None):
    for event in scheduled:
        if len(event) == 2 and event[1] == "Idle":
            print(f"Time {event[0]:>3} : Idle")
        elif event[2] == "arrived":
            print(f"Time {event[0]:>3} : {event[1]} arrived")
        elif event[2] == "selected":
            print(f"Time {event[0]:>3} : {event[1]} selected (burst {event[3]:>3})")
        elif event[2] == "finished":
            print(f"Time {event[0]:>3} : {event[1]} finished")
            process = next((p for p in processes if p.name == event[1]), None)
            if process:
                wait_time = (process.finish_time - process.arrival - process.burst)
                turnaround_time = process.finish_time - process.arrival
                response_time = process.start_time - process.arrival
                print(f"{process.name} wait {wait_time:>3} turnaround {turnaround_time:>3} response {response_time:>3}")
    
    if total_time < run_for:
        print(f"Time {total_time}: Idle")
    print(f"Finished at time {run_for}\n")

    if process_map:
        for p in sorted(process_map.values(), key=lambda x: x.name):
            wait_time = (p.finish_time - p.arrival - p.burst)
            turnaround_time = p.finish_time - p.arrival
            response_time = p.start_time - p.arrival
            print(f"{p.name} wait {wait_time} turnaround {turnaround_time} response {response_time}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scheduler.py <input_file>")
        return

    input_file = sys.argv[1]
    
    processes = []
    time_slice = None
    algorithm = None
    global run_for
    run_for = 0

    with open(input_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if parts[0] == "processcount":
                process_count = int(parts[1])
            elif parts[0] == "runfor":
                run_for = int(parts[1])
            elif parts[0] == "use":
                algorithm = parts[1]
            elif parts[0] == "quantum":
                time_slice = int(parts[1])
            elif parts[0] == "process":
                name = parts[2]
                arrival = int(parts[4])
                burst = int(parts[6])
                processes.append(Process(name, arrival, burst))
            elif parts[0] == "end":
                break

    print(f"{len(processes)} processes")

    if algorithm == "rr":
        print("Using Round Robin Scheduling")
        if time_slice is not None:
            print(f"Quantum {time_slice}\n")
        scheduled, total_time, process_map = round_robin_scheduling(processes, time_slice, run_for)
        print_scheduling(scheduled, total_time, processes, process_map)

if __name__ == "__main__":
    main()
