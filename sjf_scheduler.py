import sys

class Process:
    def __init__(self, name: str, arrival: int, burst: int):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_burst = burst
        self.start_time = None
        self.finish_time = None

    def __repr__(self):
        return f"Process(name='{self.name}', arrival={self.arrival}, burst={self.burst}, remaining_burst={self.remaining_burst})"

def calculate_metrics(processes, runtime):
    metrics = []
    for process in processes:
        if process.start_time is None:
            metrics.append(f"{process.name} was never selected")
        elif process.finish_time is None or process.finish_time > runtime:
            metrics.append(f"{process.name} did not finish")
        else:
            wait_time = (process.finish_time - process.arrival) - process.burst
            turnaround_time = process.finish_time - process.arrival
            response_time = process.start_time - process.arrival
            metrics.append(f"{process.name} wait {wait_time} turnaround {turnaround_time} response {response_time}")
    return metrics

def preemptive_sjf(original_processes, runtime):
    output = []

    # Add the number of processes and the scheduling algorithm being used to the output
    output.append(f"\t{len(original_processes)} processes")
    output.append("Using preemptive Shortest Job First")

    # Create a copy of the processes list and sort the copy by arrival time
    processes = original_processes.copy()
    processes.sort(key=lambda x: x.arrival)
    
    current_time = 0
    ready_queue = []
    current_process = None
    event_log = []

    while current_time < runtime:
        # Handle arriving processes
        while processes and processes[0].arrival <= current_time:
            process = processes.pop(0)
            ready_queue.append(process)
            event_log.append((current_time, 'arrived', process.name))

        # Sort ready queue by remaining burst time and possibly preempt current process
        if ready_queue:
            ready_queue.sort(key=lambda x: x.remaining_burst)
            if not current_process or (ready_queue and ready_queue[0].remaining_burst < current_process.remaining_burst):
                if current_process:
                    ready_queue.append(current_process)
                current_process = ready_queue.pop(0)
                if current_process.start_time is None:
                    current_process.start_time = current_time
                event_log.append((current_time, 'selected', current_process.name, current_process.remaining_burst))

        # Execute current process
        if current_process:
            current_process.remaining_burst -= 1
            if current_process.remaining_burst == 0:
                current_process.finish_time = current_time + 1
                event_log.append((current_time + 1, 'finished', current_process.name))
                current_process = None

        # Move time forward
        current_time += 1

        # Check if the system is idle
        if current_process is None and not ready_queue and not any(process.arrival <= current_time for process in processes):
            event_log.append((current_time, 'idle'))

    # Sort events by time and priority
    event_log.sort(key=lambda x: (x[0], {'arrived': 0, 'finished': 1, 'selected': 2, 'idle': 3}[x[1]]))
    
    # Add the timeline as a table to the output
    for time in range(runtime):
        events_at_time = [event for event in event_log if event[0] == time]
        if events_at_time:
            for event in events_at_time:
                if event[1] == 'arrived':
                    output.append(f"Time {time:3d} : {event[2]} {event[1]}")
                elif event[1] == 'finished':
                    output.append(f"Time {time:3d} : {event[2]} {event[1]}")
                elif event[1] == 'selected':
                    output.append(f"Time {time:3d} : {event[2]} {event[1]} (burst {event[3]:3d})")
                elif event[1] == 'idle':
                    output.append(f"Time {time:3d} : Idle")

    output.append(f"Finished at time {runtime:3d}\n")

    # Calculate and add wait time, turnaround time, and response time for each process to the output
    metrics = calculate_metrics(original_processes, runtime)
    output.extend(metrics)

    return output

def parse_input_file(filename):
    processes = []
    runtime = None
    scheduling_algorithm = None

    with open(filename, 'r') as file:
        for line in file:
            parts = line.split()
            if parts[0] == 'processcount':
                process_count = int(parts[1])
            elif parts[0] == 'runfor':
                runtime = int(parts[1])
            elif parts[0] == 'use':
                scheduling_algorithm = parts[1]
            elif parts[0] == 'process':
                name = parts[2]
                arrival = int(parts[4])
                burst = int(parts[6])
                processes.append(Process(name, arrival, burst))
            elif parts[0] == 'end':
                break

    return processes, runtime, scheduling_algorithm

def write_output_file(filename, output):
    output_file = filename.rsplit('.', 1)[0] + '.out'
    with open(output_file, 'w') as file:
        file.write('\n'.join(output))

def main():
    if len(sys.argv) != 2:
        print("Usage: python scheduler.py <input_file>")
        return

    input_file = sys.argv[1]
    processes, runtime, scheduling_algorithm = parse_input_file(input_file)

    if scheduling_algorithm == 'sjf':
        output = preemptive_sjf(processes, runtime)
        write_output_file(input_file, output)
    else:
        print("Unsupported scheduling algorithm:", scheduling_algorithm)

if __name__ == "__main__":
    main()
