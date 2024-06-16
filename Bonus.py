# Authors: 
# Dilly Jacques
# Faramarz Aboutalebi
# Franco Molina
# Megan Bailey

import webbrowser
import os
import sys
from collections import deque

# First-Come, First-Served (FIFO)
class Process:
    def __init__(self, name: str, arrival: int, burst: int):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_burst = burst
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
            # Fix the calculation of wait time
            wait_time = process.finish_time - process.arrival - process.burst
            turnaround_time = process.finish_time - process.arrival
            response_time = process.start_time - process.arrival
            # Manually set the white spaces
            metrics.append(f"{process.name} {format_time('wait', wait_time)} {format_time('turnaround', turnaround_time)} {format_time('response', response_time)}")
    return metrics

# manually adding the function below to take care of the white space 
def format_time(string, number): 
    if string == "processes":
        number_str = str(number)
        if len(number_str) == 1:
            spaces = "  "
        elif len(number_str) == 2:
            spaces = " "
        else:
            spaces = ""
        return f"{spaces}{number} {string}"
    
    number_str = str(number)
    if len(number_str) == 1:
        spaces = "   "
    elif len(number_str) == 2:
        spaces = "  "
    else:
        spaces = " "
    return f"{string}{spaces}{number}"


def fifo_scheduling(processes, runtime):
    output = []
    # manually fix the white spaces
    output.append(format_time('processes', len(processes)))
    output.append("Using First-Come First-Served")

    sorted_processes = sorted(processes, key=lambda x: x.arrival)
    current_time = 0
    event_log = []

    for process in sorted_processes:
        event_log.append((process.arrival, 'arrived', process.name))
        if current_time < process.arrival:
            current_time = process.arrival
        
        process.start_time = current_time
        process.finish_time = process.start_time + process.burst
        event_log.append((process.start_time, 'selected', process.name, process.burst))
        event_log.append((process.finish_time, 'finished', process.name))
        current_time = process.finish_time

    event_log.sort(key=lambda x: (x[0], {'arrived': 0, 'finished': 1, 'selected': 2}[x[1]]))
    selected_processes = set()
    for time in range(runtime):
        events_at_time = [event for event in event_log if event[0] == time]
        if events_at_time:
            for event in events_at_time:
                if event[1] == 'arrived':
                    output.append(f"{format_time('Time', time)} : {event[2]} {event[1]}")
                elif event[1] == 'finished':
                    selected_processes.discard(event[2])
                    output.append(f"{format_time('Time',time)} : {event[2]} {event[1]}")
                    if [e[0] for e in event_log].count(time) == 1 and not selected_processes:
                        output.append(f"{format_time('Time', time)} : Idle")
                elif event[1] == 'selected':
                    selected_processes.add(event[2])
                    output.append(f"{format_time('Time', time)} : {event[2]} {event[1]} (burst   {event[3]})")
        else:
            if not selected_processes:
                output.append(f"{format_time('Time', time)} : Idle")

    output.append(f"Finished at time  {runtime}\n")
    output.extend(calculate_metrics(processes, runtime))

    return output

# Pre-emptive Shortest Job First (SJF)
def preemptive_sjf(original_processes, runtime):
    output = []
    # manually fix the white space
    
    output.append(format_time('processes', len(original_processes)))
    output.append("Using preemptive Shortest Job First")

    processes = original_processes.copy()
    processes.sort(key=lambda x: x.arrival)
    current_time = 0
    ready_queue = []
    current_process = None
    event_log = []

    while current_time < runtime:
        while processes and processes[0].arrival <= current_time:
            process = processes.pop(0)
            ready_queue.append(process)
            event_log.append((current_time, 'arrived', process.name))

        if ready_queue:
            ready_queue.sort(key=lambda x: x.remaining_burst)
            if not current_process or (ready_queue and ready_queue[0].remaining_burst < current_process.remaining_burst):
                if current_process:
                    ready_queue.append(current_process)
                current_process = ready_queue.pop(0)
                if current_process.start_time is None:
                    current_process.start_time = current_time
                event_log.append((current_time, 'selected', current_process.name, current_process.remaining_burst))

        if current_process:
            current_process.remaining_burst -= 1
            if current_process.remaining_burst == 0:
                current_process.finish_time = current_time + 1
                event_log.append((current_time + 1, 'finished', current_process.name))
                current_process = None

        current_time += 1
        if current_process is None and not ready_queue and not any(process.arrival <= current_time for process in processes):
            event_log.append((current_time, 'idle'))

    event_log.sort(key=lambda x: (x[0], {'arrived': 0, 'finished': 1, 'selected': 2, 'idle': 3}[x[1]]))
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
    metrics = calculate_metrics(original_processes, runtime)
    output.extend(metrics)

    return output

# Round Robin (RR)
def round_robin_scheduling(processes, time_slice, run_for):
    queue = deque()
    processes.sort(key=lambda x: x.arrival)
    time = 0
    scheduled = []
    process_map = {p.name: p for p in processes}

    while time < run_for:
        while processes and processes[0].arrival <= time:
            arriving_process = processes.pop(0)
            scheduled.append((time, arriving_process.name, "arrived"))
            queue.append(arriving_process)

        if queue:
            current_process = queue.popleft()
            if current_process.start_time is None:
                current_process.start_time = time

            run_time = min(current_process.remaining_burst, time_slice)
            scheduled.append((time, current_process.name, "selected", current_process.remaining_burst))

            for _ in range(run_time):
                time += 1
                current_process.remaining_burst -= 1
                while processes and processes[0].arrival <= time:
                    arriving_process = processes.pop(0)
                    scheduled.append((time, arriving_process.name, "arrived"))
                    queue.append(arriving_process)

                if time >= run_for:
                    break

            if current_process.remaining_burst == 0:
                current_process.finish_time = time
                scheduled.append((time, current_process.name, "finished"))
                if time < run_for and (not queue and not any(process.arrival <= time for process in processes)):
                    scheduled.append((time, "Idle"))  # Add idle only if no process is ready to run
            else:
                queue.append(current_process)
        else:
            if processes:
                time = processes[0].arrival
            else:
                time += 1
                if time < run_for:  # Ensure Idle is added only within the run_for time
                    scheduled.append((time, "Idle"))

    return scheduled, time, process_map

def print_scheduling(scheduled, total_time, processes, run_for, process_map=None):
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
                print(f"{process.name} wait   {wait_time:>3} turnaround   {turnaround_time:>3} response   {response_time:>3}")
    
    if total_time < run_for:
        print(f"Time {total_time}: Idle")
    print(f"Finished at time {run_for}\n")

    if process_map:
        for p in sorted(process_map.values(), key=lambda x: x.name):
            wait_time = (p.finish_time - p.arrival - p.burst)
            turnaround_time = p.finish_time - p.arrival
            response_time = p.start_time - p.arrival
            print(f"{p.name} {format_time('wait', wait_time)} {format_time('turnaround', turnaround_time)} {format_time('response', response_time)}")
            
            
def parse_input_file(filename):
    processes = []
    runtime = None
    scheduling_algorithm = None
    time_slice = None

    with open(filename, 'r') as file:
        for line in file:
            parts = line.split()
            if parts[0] == 'processcount':
                process_count = int(parts[1])
            elif parts[0] == 'runfor':
                runtime = int(parts[1])
            elif parts[0] == 'use':
                scheduling_algorithm = parts[1]
            elif parts[0] == 'quantum':
                time_slice = int(parts[1])
            elif parts[0] == 'process':
                name = parts[2]
                arrival = int(parts[4])
                burst = int(parts[6])
                processes.append(Process(name, arrival, burst))
            elif parts[0] == 'end':
                break

    return processes, runtime, scheduling_algorithm, time_slice

def write_output_file(filename, output):
    output_file = filename.split('.')[0] + '.out'
    html_file = filename.split('.')[0] + '.html'

    with open(output_file, 'w') as file:
        file.write('\n'.join(output))
        file.write('\n')

    html_output = """
    <html>
    <head>
        <title>Scheduling Results</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <h1>Scheduling Results</h1>
        <table>
            <tr>
                <th>Time</th>
                <th>Event</th>
            </tr>
    """
    
    for line in output:
        if line.startswith("Time") or "Idle" in line:
            parts = line.split(':')
            html_output += f"<tr><td>{parts[0]}</td><td>{parts[1]}</td></tr>\n"
        else:
            html_output += f"<tr><td colspan='2'>{line}</td></tr>\n"

    html_output += "</table></body></html>"

    with open(html_file, 'w') as file:
        file.write(html_output)

    return os.path.abspath(html_file)


def write_scheduling_to_file(file, scheduled, total_time, processes, run_for, process_map=None):
    html_output = """
    <html>
    <head>
        <title>Scheduling Results</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <h1>Scheduling Results</h1>
        <table>
            <tr>
                <th>Time</th>
                <th>Event</th>
            </tr>
    """

    for event in scheduled:
        if len(event) == 2 and event[1] == "Idle":
            file.write(f"Time {event[0]:>3} : Idle\n")
            html_output += f"<tr><td>{event[0]:>3}</td><td>Idle</td></tr>\n"
        elif event[2] == "arrived":
            file.write(f"Time {event[0]:>3} : {event[1]} arrived\n")
            html_output += f"<tr><td>{event[0]:>3}</td><td>{event[1]} arrived</td></tr>\n"
        elif event[2] == "selected":
            file.write(f"Time {event[0]:>3} : {event[1]} selected (burst {event[3]:>3})\n")
            html_output += f"<tr><td>{event[0]:>3}</td><td>{event[1]} selected (burst {event[3]:>3})</td></tr>\n"
        elif event[2] == "finished":
            file.write(f"Time {event[0]:>3} : {event[1]} finished\n")
            html_output += f"<tr><td>{event[0]:>3}</td><td>{event[1]} finished</td></tr>\n"
            process = next((p for p in processes if p.name == event[1]), None)
            if process:
                wait_time = (process.finish_time - process.arrival - process.burst)
                turnaround_time = process.finish_time - process.arrival
                response_time = process.start_time - process.arrival
                file.write(f"{process.name} wait {wait_time:>3} turnaround {turnaround_time:>3} response {response_time:>3}\n")
                html_output += f"<tr><td colspan='2'>{process.name} wait {wait_time:>3} turnaround {turnaround_time:>3} response {response_time:>3}</td></tr>\n"
    
    if total_time < run_for:
        file.write(f"Time {total_time}: Idle\n")
        html_output += f"<tr><td>{total_time}</td><td>Idle</td></tr>\n"
    file.write(f"Finished at time  {run_for}\n")
    html_output += f"<tr><td colspan='2'>Finished at time {run_for}</td></tr>\n"

    html_output += "</table>"

    if process_map:
        html_output += """
        <h2>Process Metrics</h2>
        <table>
            <tr>
                <th>Process</th>
                <th>Wait Time</th>
                <th>Turnaround Time</th>
                <th>Response Time</th>
            </tr>
        """
        for p in sorted(process_map.values(), key=lambda x: x.name):
            wait_time = (p.finish_time - p.arrival - p.burst)
            turnaround_time = p.finish_time - p.arrival
            response_time = p.start_time - p.arrival
            file.write(f"{p.name} {format_time('wait', wait_time)} {format_time('turnaround', turnaround_time)} {format_time('response', response_time)}\n")
            html_output += f"<tr><td>{p.name}</td><td>{wait_time}</td><td>{turnaround_time}</td><td>{response_time}</td></tr>\n"

        html_output += "</table>\n"

    html_output += "</body>\n</html>"

    # Write the HTML output to a file
    html_file = file.name.replace('.out', '.html')
    with open(html_file, 'w') as f:
        f.write(html_output)

    return os.path.abspath(html_file)

def main():
    if len(sys.argv) != 2:
        print("Usage: python scheduler.py <input_file>")
        return

    input_file = sys.argv[1]
    processes, runtime, scheduling_algorithm, time_slice = parse_input_file(input_file)

    if scheduling_algorithm == 'fcfs':
        output = fifo_scheduling(processes, runtime)
        html_file = write_output_file(input_file, output)
        webbrowser.open(f"file://{html_file}")  # Open the HTML file in a web browser
    elif scheduling_algorithm == 'sjf':
        output = preemptive_sjf(processes, runtime)
        html_file = write_output_file(input_file, output)
        webbrowser.open(f"file://{html_file}")  # Open the HTML file in a web browser
    elif scheduling_algorithm == 'rr':
        output_file = input_file.split('.')[0] + '.out'
        with open(output_file, 'w') as file:
            file.write(format_time('processes', len(processes)) + '\n')
            file.write("Using Round-Robin\n")
            if time_slice is not None:
                file.write(f"Quantum   {time_slice}\n\n")
            scheduled, total_time, process_map = round_robin_scheduling(processes, time_slice, runtime)
            html_file = write_scheduling_to_file(file, scheduled, total_time, processes, runtime, process_map)
            webbrowser.open(f"file://{html_file}")  # Open the HTML file in a web browser
    else:
        print("Unsupported scheduling algorithm:", scheduling_algorithm)

if __name__ == "__main__":
    main()
