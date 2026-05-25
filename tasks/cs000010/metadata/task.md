## Background

This assignment is to build `stsh`, the Stanford Shell. You will extend a basic shell framework to support job control, including running processes in the foreground and background, managing jobs, handling signals, and implementing pipelines and I/O redirection.

By completing this assignment, you will:
- Gain a deep understanding of process management, including process creation, reaping, and process groups.
- Learn how to handle signals like `SIGCHLD`, `SIGINT`, and `SIGTSTP`.
- Understand how shells implement complex features like pipelines and I/O redirection.
- Get more experience with C++ and systems programming.

You are provided with a skeleton for `stsh` in `stsh.cc`, along with a parser and other utility files. Your main task is to implement the core job control logic within `stsh.cc`.

The `main` function loop is provided:
```cpp
int main(int argc, char *argv[]) {
  pid_t stshpid = getpid();
  installSignalHandlers();
  rlinit(argc, argv); // configures stsh-readline library so readline works properly
  while (true) {
    string line;
    if (!readline(line)) break;
    if (line.empty()) continue;
    try {
      pipeline p(line);
      bool builtin = handleBuiltin(p);
      if (!builtin) createJob(p); // createJob is initially defined as a wrapper around cout << p;
    } catch (const STSHException& e) {
      cerr << e.what() << endl;
      if (getpid() != stshpid) exit(0); // if exception is thrown from child process, kill it
    }
  }
  return 0;
}
```

The parser provides you with a `pipeline` struct:
```cpp
struct pipeline {
  std::string input;   // empty if no input redirection file to first command
  std::string output;  // empty if no output redirection file from last command
  std::vector<command> commands;
  bool background;
  
  pipeline(const std::string& str);
  ~pipeline();
};
```

## Your Task: Implement Job Control

Your primary goal is to implement the logic for handling jobs and built-in commands. The built-ins `quit`, `exit`, and `jobs` are already implemented for you. You must implement the following:

*   **`fg <job>`**: Resumes a stopped job or brings a background job to the foreground.
*   **`bg <job>`**: Resumes a stopped job in the background.
*   **`slay <job> <process>` or `slay <pid>`**: Terminates a specific process.
*   **`halt <job> <process>` or `halt <pid>`**: Stops a specific process.
*   **`cont <job> <process>` or `cont <pid>`**: Resumes a specific process in the background.

You will need to manage a list of jobs, handle signals to update job states, and correctly manage process groups and terminal control.

### Implementation Details

*   **Terminal Control**: Use the `tcsetpgrp` function to transfer terminal control to the foreground process group.
*   **Signal Handling Architecture**: `waitpid` should only be called within the `SIGCHLD` handler. Use `sigsuspend` (or similar functions) to suspend the shell main thread while waiting for signals.
*   **Job List Synchronization**: Use the `STSHJobList::synchronize` method to check and update job statuses.
*   **Specific Error Handling**: Commands like `fg` and `bg` must throw `STSHException` if arguments are invalid.

## Important Notes

*   You should only need to modify `stsh.cc`.
*   Do not declare any new global variables (constants are okay).
*   Close all unused file descriptors in child processes.
*   Ensure all processes in a pipeline are in the same process group. Call `setpgid` in both the parent and child to avoid race conditions.
*   You do not need to support pipelines or redirection for built-in commands.