#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/select.h>
#include <signal.h>
#include <getopt.h>

using namespace std;

// Function to print usage information
void print_usage(const char* prog_name) {
    cerr << "Usage: " << prog_name << " -t <tracefile> -s <shell> [-a <args>]" << endl;
}

// Function to send a line to the shell process
void send_to_shell(int pipe_fd, const string& line) {
    string full_line = line + "\n";
    write(pipe_fd, full_line.c_str(), full_line.length());
}

// Main function for the driver
int main(int argc, char* argv[]) {
    string trace_file, shell_path, shell_args;
    int opt;

    // Parse command-line arguments
    while ((opt = getopt(argc, argv, "t:s:a:")) != -1) {
        switch (opt) {
            case 't':
                trace_file = optarg;
                break;
            case 's':
                shell_path = optarg;
                break;
            case 'a':
                shell_args = optarg;
                break;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }

    if (trace_file.empty() || shell_path.empty()) {
        print_usage(argv[0]);
        return 1;
    }

    // Pipes for communication with the shell process
    int to_shell_pipe[2];
    int from_shell_pipe[2];
    pipe(to_shell_pipe);
    pipe(from_shell_pipe);

    pid_t pid = fork();

    if (pid == 0) { // Child process
        // Redirect stdin, stdout, and stderr
        dup2(to_shell_pipe[0], STDIN_FILENO);
        dup2(from_shell_pipe[1], STDOUT_FILENO);
        dup2(from_shell_pipe[1], STDERR_FILENO);

        // Close unused pipe ends
        close(to_shell_pipe[1]);
        close(from_shell_pipe[0]);

        // Prepare arguments for exec
        vector<string> shell_args_vec;
        if (!shell_args.empty()) {
            istringstream iss(shell_args);
            string arg;
            while (iss >> arg) {
                shell_args_vec.push_back(arg);
            }
        }

        vector<char*> exec_args;
        // The first argument, argv[0], is the program name.
        // By convention, this is the path used to execute it.
        exec_args.push_back(const_cast<char*>(shell_path.c_str()));

        // The -a arguments may redundantly include the shell name as the first argument.
        // If so, we skip it to avoid duplication.
        size_t start_index = 0;
        string shell_basename = shell_path.substr(shell_path.find_last_of("/") + 1);
        if (!shell_args_vec.empty() && shell_args_vec[0] == shell_basename) {
            start_index = 1;
        }

        for (size_t i = start_index; i < shell_args_vec.size(); ++i) {
            exec_args.push_back(const_cast<char*>(shell_args_vec[i].c_str()));
        }
        exec_args.push_back(nullptr);

        execvp(shell_path.c_str(), exec_args.data());
        perror("execvp failed");
        exit(1);
    } else { // Parent process
        close(to_shell_pipe[0]);
        close(from_shell_pipe[1]);

        ifstream trace(trace_file);
        string line;

        cout << "# Trace: " << trace_file << endl;
        cout << "# ------------------------" << endl;

        bool trace_has_quit = false;
        while (getline(trace, line)) {
            if (line.empty()) continue;

            // Simple handling for special commands
            if (line.rfind("&pause", 0) == 0) {
                sleep(1); // Simple pause
                continue;
            } else if (line.rfind("&signal", 0) == 0) {
                // Simplified: send SIGINT. A full implementation would parse the signal type.
                kill(pid, SIGINT);
                continue;
            }

            if (line == "quit" || line == "exit") {
                trace_has_quit = true;
            }

            send_to_shell(to_shell_pipe[1], line);
            cout << "stsh> " << line << endl;

            // Add a small delay to allow the shell to process the command
            usleep(200000); // 200ms

            // Read output from the shell with multiple iterations to drain all output
            for (int i = 0; i < 10; i++) {
                fd_set read_fds;
                FD_ZERO(&read_fds);
                FD_SET(from_shell_pipe[0], &read_fds);

                struct timeval timeout;
                timeout.tv_sec = 0;
                timeout.tv_usec = 50000; // 50ms timeout

                if (select(from_shell_pipe[0] + 1, &read_fds, nullptr, nullptr, &timeout) > 0) {
                    char buffer[4096];
                    ssize_t count = read(from_shell_pipe[0], buffer, sizeof(buffer) - 1);
                    if (count > 0) {
                        buffer[count] = '\0';
                        cout << buffer;
                    } else {
                        break;
                    }
                } else {
                    break;
                }
            }

            // If quit was sent, close pipe immediately to trigger EOF
            // This ensures readline detects EOF and shell can exit properly
            if (trace_has_quit) {
                usleep(200000); // 200ms delay to ensure quit is processed
                close(to_shell_pipe[1]); // Close pipe to signal EOF
                break;
            }
        }

        // If trace file didn't have quit, send it now
        if (!trace_has_quit) {
            send_to_shell(to_shell_pipe[1], "quit");
            cout << "stsh> quit" << endl;
            usleep(200000); // 200ms delay for shell to process
            close(to_shell_pipe[1]); // Close pipe to signal EOF
        }

        // Wait for shell to exit with a reasonable timeout
        int status;
        for (int i = 0; i < 20; i++) {
            pid_t result = waitpid(pid, &status, WNOHANG);
            if (result == pid) {
                break; // Process exited
            }
            if (result == -1) {
                break; // Error
            }
            usleep(100000); // 100ms between checks, total 2 seconds max
        }
        
        // If still running, do blocking wait
        waitpid(pid, &status, 0);

        close(from_shell_pipe[0]);
    }

    return 0;
}