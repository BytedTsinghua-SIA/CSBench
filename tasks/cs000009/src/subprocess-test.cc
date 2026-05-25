/**
 * File: subprocess-test.cc
 * ------------------------
 * Simple unit test framework in place to exercise functionality of the subprocess function.
 */

#include "subprocess.h"
#include <iostream>
#include <fstream>
#include <string>
#include <sys/wait.h>
#include <cstdio>
using namespace std;

/**
 * File: publishWordsToChild
 * -------------------------
 * Algorithmically self-explanatory.  Relies on a g++ extension where iostreams can
 * be wrapped around file desriptors so that we can use operator<<, getline, endl, etc.
 */
const string kWords[] = {"put", "a", "ring", "on", "it"};
static void publishWordsToChild(int to) {
  FILE* fp = fdopen(to, "w");
  if (fp == NULL) return;
  for (const string& word: kWords) {
    fprintf(fp, "%s\n", word.c_str());
  }
  fclose(fp); // closes the underlying descriptor
}
    
/**
 * File: ingestAndPublishWords
 * ---------------------------
 * Reads in everything from the provided file descriptor, which should be
 * the sorted content that the child process running /usr/bin/sort publishes to
 * its standard out.  Note that we one again rely on the same g++ extenstion that
 * allows us to wrap an iostream around a file descriptor so we have C++ stream semantics
 * available to us.
 */
static void ingestAndPublishWords(int from) {
  FILE* fp = fdopen(from, "r");
  if (fp == NULL) return;
  char buffer[1024];
  while (fgets(buffer, sizeof(buffer), fp) != NULL) {
    // strip trailing newline if present
    string word(buffer);
    if (!word.empty() && word.back() == '\n') word.pop_back();
    cout << word << endl;
  }
  fclose(fp);
}

/**
 * Function: waitForChildProcess
 * -----------------------------
 * Halts execution until the process with the provided id exits.
 */
static void waitForChildProcess(pid_t pid) {
  if (waitpid(pid, NULL, 0) != pid) {
    throw SubprocessException("Encountered a problem while waiting for subprocess's process to finish.");
  }
}

/**
 * Function: main
 * --------------
 * Serves as the entry point for for the unit test.
 */
const string kSortExecutable = "/usr/bin/sort";
int main(int argc, char *argv[]) {
  try {
    char *argv[] = {const_cast<char *>(kSortExecutable.c_str()), NULL};
    subprocess_t child = subprocess(argv, true, true);
    publishWordsToChild(child.supplyfd);
    ingestAndPublishWords(child.ingestfd);
    waitForChildProcess(child.pid);
    return 0;
  } catch (const SubprocessException& se) {
    cerr << "Problem encountered while spawning second process to run \"" << kSortExecutable << "\"." << endl;
    cerr << "More details here: " << se.what() << endl;
    return 1;
  } catch (...) { // ... here means catch everything else
    cerr << "Unknown internal error." << endl;
    return 2;
  }
}
