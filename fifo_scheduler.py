import sys

class Process:
    def __init__(self, name: str, arrival: int, burst: int):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.start_time = None
        self.finish_time = None

    def __repr__(self):
        return f"Process(name='{self.name}', arrival={self.arrival}, burst={self.burst})"

def calculate_metrics(processes, runtime):
    metrics = []
    for process in processes:
        if process.start_time is None:
            metrics.append(f"{process.name} was never selected")
        elif process.finish_time is None or process.finish_time > runtime:
            metrics.append(f"{process.name} did not finish")
        else:
            wait_time = process.start_time - process.arrival
            turnaround_time = process.finish_time - process.arrival
            response_time = process.start_time - process.arrival
            metrics.append(f"{process.name} wait {wait_time} turnaround {turnaround_time} response {response_time}")
    return metrics

def fifo_scheduling(processes, runtime):
    output = []

    # Add the number of processes and the scheduling algorithm being used to the output
    output.append(f"{len(processes)} processes")
    output.append("Using First In First Out")

    # Create a copy of the processes list and sort the copy by arrival time
    sorted_processes = sorted(processes, key=lambda x: x.arrival)
    
    current_time = 0
    event_log = []

    for process in sorted_processes:
        # Record the arrival event
        event_log.append((process.arrival, 'arrived', process.name))
        
        # If the current time is less than the process's arrival time, wait until it arrives
        if current_time < process.arrival:
            current_time = process.arrival
        
        # Record the start and finish times
        process.start_time = current_time
        process.finish_time = process.start_time + process.burst
        
        # Record the time the process is selected and finished
        event_log.append((process.start_time, 'selected', process.name, process.burst))
        event_log.append((process.finish_time, 'finished', process.name))

        # Update current time
        current_time = process.finish_time

    # Sort events by time and priority
    event_log.sort(key=lambda x: (x[0], {'arrived': 0, 'finished': 1, 'selected': 2}[x[1]]))
    
    # Add the timeline as a table to the output
    selected_processes = set()
    for time in range(runtime):
        events_at_time = [event for event in event_log if event[0] == time]
        if events_at_time:
            for event in events_at_time:
                if event[1] == 'arrived':
                    output.append(f"Time {time}: {event[2]} {event[1]}")
                elif event[1] == 'finished':
                    selected_processes.discard(event[2])
                    output.append(f"Time {time}: {event[2]} {event[1]}")
                    # Check if the scheduler will be idle at the next time tick
                    # HUMAN COMMENT: I modified the logic on the line below. The AI generated
                    # code was producing incorrect output as it would print Idle even if the
                    # system was not going to become idle. Instead of checking to find if any
                    # number of events occur at a time, we check to see if exactly one event
                    # occurs at the time.
                    if [e[0] for e in event_log].count(time) == 1 and not selected_processes:                        output.append(f"Time {time}: Idle")
                elif event[1] == 'selected':
                    selected_processes.add(event[2])
                    output.append(f"Time {time}: {event[2]} {event[1]} (burst {event[3]})")
        else:
            if not selected_processes:
                output.append(f"Time {time}: Idle")

    output.append(f"Finished at time {runtime}")

    # Calculate and add wait time, turnaround time, and response time for each process to the output
    output.extend(calculate_metrics(processes, runtime))

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
    output_file = filename.split('.')[0] + '.out'
    with open(output_file, 'w') as file:
        file.write('\n'.join(output))

def main():
    if len(sys.argv) != 2:
        print("Usage: python scheduler.py <input_file>")
        return

    input_file = sys.argv[1]
    processes, runtime, scheduling_algorithm = parse_input_file(input_file)

    if scheduling_algorithm == 'fcfs':
        output = fifo_scheduling(processes, runtime)
        write_output_file(input_file, output)
    else:
        print("Unsupported scheduling algorithm:", scheduling_algorithm)

if __name__ == "__main__":
    main()
